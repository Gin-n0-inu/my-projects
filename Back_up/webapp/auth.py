from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import mysql.connector
import mysql.connector.cursor
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from . import mysql  # Assuming mysql is initialized in __init__.py
from .models import User
from datetime import datetime
from flask import current_app  # Import for logging within the app context
from datetime import datetime, timedelta



auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        con = mysql.connection.cursor()
       # Corrected SQL query
        con.execute("SELECT user_id, is_admin FROM staff_info WHERE username = %s AND password = %s", (username, password))
        user = con.fetchone()  # Fetch one result
        con.close()

        if user:
            user_obj = User(user_id=user[0], is_admin=user[1])
            login_user(user_obj)  # Log in the user

            # Check if user is an admin
            if user[1] == 0:
                return redirect(url_for('views.track'))
            elif user[1] == 2:
                return redirect(url_for('views.reg'))
            else:
                return redirect(url_for('views.staff'))
        else:
            flash("Invalid username or password", "danger")
    


    return render_template('login.html')
    

@auth.route('/logout')
@login_required
def logout():
    # Clear all existing flash messages
    session.pop('_flashes', None)
      # Use Flask-Login's logout_user function to log out
    flash("You have been logged out.", "danger")
    logout_user()
    return redirect(url_for('auth.login'))

# Admin Dashboard Route
@auth.route('/admin-dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    con = mysql.connection.cursor()
    query = """
        SELECT process_id, tracking_code, rqtr_name, doc_info, date_time, status, location
        FROM process
    """
    params = []

    # Handling search query if present
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            query += """
                WHERE process_id = %s
                OR tracking_code LIKE %s
                OR rqtr_name LIKE %s
                OR doc_info LIKE %s
                OR location LIKE %s
            """
            params = [search_query, f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"]

    con.execute(query, params)
    process_data = con.fetchall()
    con.close()

    return render_template('admin.html', process_data=process_data)

@auth.route('/sign-up')
@login_required
def sign_up():
    user_id = request.args.get('user_id')
    con = mysql.connection.cursor()

    # Retrieve all staff data for the list
    con.execute("SELECT user_id, last_name, first_name, username, password, sys_location, is_admin FROM staff_info")
    staff_data = con.fetchall()

    # Retrieve specific user data if editing
    selected_user = None
    if user_id:
        con.execute("SELECT user_id, last_name, first_name, middle_name, username, sys_location, is_admin FROM staff_info WHERE user_id = %s", (user_id,))
        selected_user = con.fetchone()

    con.close()
    return render_template("bregister.html", staff_data=staff_data, selected_user=selected_user)

@auth.route('/save-user', methods=['POST'])
@login_required
def save_user():
    user_id = request.form.get('user_id')
    lname, fname, uname = request.form['lname'], request.form['fname'], request.form['uname']
    password1, password2 = request.form['upassword1'], request.form['upassword2']
    sys_location = request.form['syslocation']
    is_admin = 1 if request.form['is_admin'] == "true" else 0

    if password1 != password2:
        flash("Passwords do not match")
        return redirect(url_for('auth.sign_up')) 

    cursor = mysql.connection.cursor()
    
    # Update if user_id exists; else insert as a new record
    if user_id:
        cursor.execute("""
            UPDATE staff_info
            SET last_name = %s, first_name = %s, username = %s, password = %s, 
                sys_location = %s, is_admin = %s
            WHERE user_id = %s
        """, (lname, fname, uname, password1, sys_location, is_admin, user_id))
        
    else:
        cursor.execute("""
            INSERT INTO staff_info (last_name, first_name, username, password, sys_location, is_admin)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (lname, fname, uname, password1, sys_location, is_admin))
        
    
    mysql.connection.commit()
    cursor.close()
    
    flash("User saved successfully")
    return redirect(url_for('auth.sign_up'))

@auth.route('/administrator', methods=['GET','POST'])
@login_required  # Protect this route
def administrator():
    con = mysql.connection.cursor()

     # Get user location based on user ID
    con.execute("SELECT sys_location FROM staff_info WHERE user_id = %s", (current_user.id,))
    user_location = con.fetchone()  # Assume location is in the first column
    user_location = user_location[0] if user_location else "Location not found"
    
    # Check if a search request was made (if `POST` request with `search-input`)
    tracking_code = request.form.get('search-input')

     # Check if update request is made
    tracking_code_to_update = request.form.get('update_data')

    # Check if complete request was made for status
    tracking_code_to_complete = request.form.get('complete_data')

    tracking_code_to_transfer = request.form.get('transfer_data')

    if tracking_code_to_transfer:
        # Update status in the process table for the given tracking code
        try:
            con.execute(
                """
                UPDATE process 
                SET status = %s 
                WHERE tracking_code = %s
                """, 
                ("Transfer", tracking_code_to_transfer)
            )
            mysql.connection.commit()
            flash(f"Status updated to 'Completed' for tracking code {tracking_code_to_transfer}.", 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Failed to mark as complete: {e}", 'danger')

     # Check if update request is made
    tracking_code_to_update = request.form.get('update_data')

    if tracking_code_to_complete:
        # Update status in the process table for the given tracking code
        try:
            con.execute(
                """
                UPDATE process 
                SET status = %s 
                WHERE tracking_code = %s
                """, 
                ("Completed", tracking_code_to_complete)
            )
            mysql.connection.commit()
            flash(f"Status updated to 'Completed' for tracking code {tracking_code_to_complete}.", 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Failed to mark as complete: {e}", 'danger')

    if tracking_code_to_update:
        # Update location in the process table for the given tracking code
        try:
            con.execute(
                """
                UPDATE process 
                SET location = %s, status = %s
                WHERE tracking_code = %s
                """, 
                (user_location, 'Pending', tracking_code_to_update)
            )
            mysql.connection.commit()
            flash(f"Location updated to '{user_location}' for tracking code {tracking_code_to_update}.", 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Failed to update location: {e}", 'danger')
    
    if tracking_code:  # If there's a search query
        # Query for the specific tracking code
        con.execute(
            """
            SELECT process_id, tracking_code, rqtr_name, doc_info, date_time, status, location
            FROM process
            WHERE tracking_code = %s
            """, (tracking_code,)
        )
        process_data = con.fetchall()  # Fetch matching rows
        
        # If no results are found, show a flash message
        if not process_data:
            flash('No records found for the provided tracking code.', 'warning')
    else:  # If there's no search query, fetch all data
        con.execute(
            """
            SELECT process_id, tracking_code, rqtr_name, doc_info, date_time, status, location
            FROM process
            """
        )
        process_data = con.fetchall()  # Fetch all rows

        # Fetch counts for each status
    con.execute("SELECT status, COUNT(*) FROM process GROUP BY status")
    status_counts = dict(con.fetchall())

                # Ensure all status types are present
    for status in ["Pending", "Transfer", "Completed"]:
            if status not in status_counts:
                status_counts[status] = 0

    # Calculate total count
    total_count = sum(status_counts.values())

    con.close()  # Close the database connection
    
    return render_template('search.html', process_data=process_data, user_location=user_location, status_counts=status_counts,total_count=total_count)

@auth.route('/delete-user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')  # Get user_id from the form
    if user_id:
        con = mysql.connection.cursor()
        con.execute("DELETE FROM staff_info WHERE user_id = %s", (user_id,))
        mysql.connection.commit()
        con.close()
        return redirect(url_for('auth.sign_up'))  # Redirect after deletion
    return redirect(url_for('auth.sign_up', error="Invalid user ID"))  # Handle errors as needed

@auth.route('/remove_process', methods=['POST'])
def remove_process():
    user_id = request.form.get('tracking_code')  # Get user_id from the form
    if user_id:
        con = mysql.connection.cursor()
        con.execute("DELETE FROM process WHERE tracking_code = %s", (user_id,))
        mysql.connection.commit()
        con.close()
        return redirect(url_for('auth.administrator'))  # Redirect after deletion
    return redirect(url_for('auth.sign_up', error="Invalid user ID"))  # Handle errors as needed

@auth.route('/doc-process')
@login_required
def process1():
    return render_template('board_admin.html')

@auth.route('/add_request', methods=['GET', 'POST'])
@login_required
def add_request():
    if request.method == 'POST':
        try:
            # Fetch the form data
            fname = request.form.get('rqtr_fname')
            mname = request.form.get('rqtr_mname')
            lname = request.form.get('rqtr_lname')
            age = request.form.get('rqtr_age')
            gender = request.form.get('rqtr_sex')
            mobile_number = request.form.get('rqtr_number')
            email = request.form.get('rqtr_email')
            doc_info = request.form.get('doc_info')
            tracking_code = request.form.get('track_code')
            date_info = request.form.get('date_time') or datetime.now().strftime("%Y-%m-%d")

            # Combine names
            rqtr_name = f"{fname} {mname} {lname}"

            # Parse date_info for weekly restriction
            request_date = datetime.strptime(date_info, "%Y-%m-%d")
            week_start = request_date - timedelta(days=request_date.weekday())  # Get the start of the week
            week_end = week_start + timedelta(days=6)  # Get the end of the week


            # Logging form data
            current_app.logger.info("Form data received: %s", request.form)

            # Establish a cursor
            cur = mysql.connection.cursor()

            # Check for existing weekly records with the same doc_info
            cur.execute(
                """
                SELECT * FROM process
                WHERE rqtr_name = %s
                AND doc_info = %s
                AND date_time BETWEEN %s AND %s
                """, (rqtr_name, doc_info, week_start, week_end)
            )
            existing_doc_request = cur.fetchone()

            # Allow adding only if there are no existing "Voucher" or "Procurement" within the same week
            if not (doc_info in ["Voucher", "Procurement"] and existing_doc_request):
                # Insert into requestor_info table

                # Insert into tables
                cur.execute(
                """
                INSERT INTO requestor_info (rqtr_fname, rqtr_mname, rqtr_lname, rqtr_age, rqtr_sex, rqtr_mobile_no, rqtr_email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (fname, mname, lname, age, gender, mobile_number, email)
            )
                cur.execute(
                """
                INSERT INTO process (tracking_code, rqtr_name, doc_info, date_time, status, location)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (tracking_code, rqtr_name, doc_info, date_info, "Pending", None)
            )

            # Commit transaction
                mysql.connection.commit()

            # Get the ID of the last inserted request <---------------------------------------------
                request_id = cur.lastrowid

                flash('Request added successfully!', 'success')

            # Redirect to the confirmation page <------------------------------------------------------
                return redirect(url_for('auth.request_confirmation', request_id=request_id))
            else:
                # If the weekly restriction is violated, flash a warning
                flash('A similar document request already exists for this client this week. Only one "Voucher" and one "Procurement" allowed per week.', 'warning')


        except Exception as err:
            mysql.connection.rollback()
            current_app.logger.error(f"Error occurred during request addition: {err}")
            flash(f"An error occurred: {err}", 'danger')

        finally:
            cur.close()

        return redirect(url_for('auth.add_request'))

    return render_template('board_admin.html')

@auth.route('/request_confirmation/<int:request_id>')
@login_required
def request_confirmation(request_id):
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT tracking_code, rqtr_name, doc_info, date_time
        FROM process
        WHERE process_id = %s
        """,
        (request_id,)
    )
    request_data = cur.fetchone()
    cur.close()

    if not request_data:
        flash('No data found for this request.', 'danger')
        return redirect(url_for('auth.add_request'))

    return render_template('request_confirmation.html', request_data=request_data)

#############################################################################

@auth.route('/staff-dashboard', methods=['GET','POST'])
@login_required
def staff_dashboard():

    con = mysql.connection.cursor()

     # Get user location based on user ID
    con.execute("SELECT sys_location FROM staff_info WHERE user_id = %s", (current_user.id,))
    user_location = con.fetchone()  # Assume location is in the first column
    user_location = user_location[0] if user_location else "Location not found"

    # Check if complete request was made for status
    tracking_code_to_transfer = request.form.get('transfer_data')

    # Check if complete request was made for status
    tracking_code_to_complete = request.form.get('complete_data')

    if tracking_code_to_complete:
        # Update status in the process table for the given tracking code
        try:
            con.execute(
                """
                UPDATE process 
                SET status = %s 
                WHERE tracking_code = %s
                """, 
                ("Completed", tracking_code_to_complete)
            )
            mysql.connection.commit()
            flash(f"Status updated to 'Completed' for tracking code {tracking_code_to_complete}.", 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Failed to mark as complete: {e}", 'danger')

    if tracking_code_to_transfer:
        # Update status in the process table for the given tracking code
        try:
            con.execute(
                """
                UPDATE process 
                SET status = %s 
                WHERE tracking_code = %s
                """, 
                ("Transfer", tracking_code_to_transfer)
            )
            mysql.connection.commit()
            flash(f"Status updated to 'Transfer' for tracking code {tracking_code_to_transfer}.", 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Failed to mark as complete: {e}", 'danger')

     # Check if update request is made
    tracking_code_to_update = request.form.get('update_data')

    if tracking_code_to_update:
        # Update location in the process table for the given tracking code
        try:
            con.execute(
                """
                UPDATE process 
                SET location = %s, status =  %s
                WHERE tracking_code = %s
                """, 
                ("Pending", user_location, tracking_code_to_update)
            )
            mysql.connection.commit()
            flash(f"Location updated to '{user_location}' for tracking code {tracking_code_to_update}.", 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Failed to update location: {e}", 'danger')


    # Check if a search request was made (if `POST` request with `search-input`)
    tracking_code = request.form.get('search-input')

    if tracking_code:  # If there's a search query
        # Query for the specific tracking code
        con.execute(
            """
            SELECT process_id, tracking_code, rqtr_name, doc_info, date_time, status, location
            FROM process
            WHERE tracking_code = %s
            """, (tracking_code,)
        )
        process_data = con.fetchall()  # Fetch matching rows
        
        # If no results are found, show a flash message
        if not process_data:
            flash('No records found for the provided tracking code.', 'warning')
    else:  # If there's no search query, fetch all data
        con.execute(
            """
            SELECT process_id, tracking_code, rqtr_name, doc_info, date_time, status, location
            FROM process
            """
        )
        process_data = con.fetchall()  # Fetch all rows

        # Fetch counts for each status
    con.execute("SELECT status, COUNT(*) FROM process GROUP BY status")
    status_counts = dict(con.fetchall())

                # Ensure all status types are present
    for status in ["Pending", "Transfer", "Completed"]:
            if status not in status_counts:
                status_counts[status] = 0

    # Calculate total count
    total_count = sum(status_counts.values())

    con.close()  # Close the database connection

    return render_template('staff_home.html', process_data=process_data, user_location=user_location, total_count=total_count,status_counts=status_counts)

@auth.route('/process-tracking', methods=['GET','POST'])
@login_required
def staff_s():

    con = mysql.connection.cursor()

    # Base query to select all columns from the process table
    query = """
        SELECT process_id, tracking_code, rqtr_name, doc_info, date_time, status, location
        FROM process
    """
    params = []

    # If a search query is provided, add conditions to check multiple fields
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            query += """
                WHERE process_id = %s
                OR tracking_code LIKE %s
                OR rqtr_name LIKE %s
                OR doc_info LIKE %s
                OR location LIKE %s
            """
            # Match process_id exactly, and perform partial matches for other fields
            params = [
                search_query,               # process_id exact match
                f"%{search_query}%",        # tracking_code partial match
                f"%{search_query}%",        # rqtr_name partial match
                f"%{search_query}%",        # doc_info partial match
                f"%{search_query}%",        # location partial match
            ]

    # Execute the query with parameters
    con.execute(query, params)
    process_data = con.fetchall()  # Fetch all matching rows
    con.close()

    return render_template('staff_search.html', process_data=process_data)

########################################################################################

@auth.route('/process-tracker', methods=['GET', 'POST'])
def doc_tracker():
    con = mysql.connection.cursor()
    process_data = []  # Initialize as empty list by default

    # Check if a search request was made (if `POST` request with `search-input`)
    tracking_code = request.form.get('search-input')

    if tracking_code:  # If there's a search query
        # Query for the specific tracking code
        con.execute(
            """
            SELECT process_id, tracking_code, rqtr_name, doc_info, date_time, status, location
            FROM process
            WHERE tracking_code = %s
            """, (tracking_code,)
        )
        process_data = con.fetchall()  # Fetch matching rows
        
        # If no results are found, show a flash message
        if not process_data:
            flash('No records found for the provided tracking code.', 'warning')

    con.close()  # Close the database connection

    return render_template('process_tracker.html', process_data=process_data)