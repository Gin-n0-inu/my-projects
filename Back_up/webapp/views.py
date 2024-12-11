from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

# admin.html
# base.html
# board_admin.html
# bregister.html
# login.html
# search.html

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("login.html")

@views.route('/admin')
 # @login_required Protect this route with login_required
def admin():
    return redirect(url_for('auth.dashboard'))

@views.route('/document-status')
@login_required 
def track(): 
    return redirect(url_for('auth.administrator'))

@views.route('/register')
@login_required
def reg():
    return redirect(url_for('auth.sign_up'))

@views.route('/add-process')
@login_required
def add1():
    return redirect(url_for('auth.process1'))

###########################################################

@views.route('/staff-dash')
@login_required
def staff():
    return redirect(url_for('auth.staff_dashboard'))

@views.route('/staff-search')
@login_required
def staff_search():
    return redirect(url_for('auth.staff_s'))

###########################################################

@views.route('/tracker')
def tracker():
    return redirect(url_for('auth.doc_tracker'))

###########################################################

