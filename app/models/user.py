from app import db, bcrypt, login
from flask_login import UserMixin
from datetime import datetime

ROLES = ('super_admin', 'admin', 'manager', 'teacher')

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role          = db.Column(db.String(20),  nullable=False, default='teacher')
    is_active     = db.Column(db.Boolean, default=True, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    created_by    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    created_users = db.relationship('User',
        backref=db.backref('creator', remote_side=[id]), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_dashboard_route(self):
        return {
            'super_admin': 'dashboard.index',
            'admin':       'dashboard.index',
            'manager':     'dashboard.index',
            'teacher':     'dashboard.index',
        }.get(self.role, 'dashboard.index')

    # convenience checks
    @property
    def is_super_admin(self): return self.role == 'super_admin'
    @property
    def is_admin_or_above(self): return self.role in ('super_admin','admin')
    @property
    def is_manager_or_above(self): return self.role in ('super_admin','admin','manager')

    def __repr__(self): return f'<User {self.username} [{self.role}]>'

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
