
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_id, is_admin):
        self.id = user_id  # This is the required attribute for Flask-Login
        self.is_admin = is_admin  # Custom attribute for your application logic