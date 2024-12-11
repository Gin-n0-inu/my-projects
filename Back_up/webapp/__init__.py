from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from .models import User

mysql = MySQL()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'm1111111111111'
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'cjunlimited011001'
    app.config['MYSQL_DB'] = 'dtsystem'

    # Initialize MySQL with app
    mysql.init_app(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Set the login route

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Define user_loader function
    @login_manager.user_loader
    def load_user(user_id):
        # Load the user from the database using user_id
        con = mysql.connection.cursor()
        con.execute("SELECT user_id, is_admin FROM staff_info WHERE user_id = %s", (user_id,))
        user_data = con.fetchone()
        con.close()
        if user_data:
            return User(user_id=user_data[0], is_admin=user_data[1])
        return None
    

    return app
