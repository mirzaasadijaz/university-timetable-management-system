"""Run once to create the initial Super Admin account."""
from app import create_app, db
from app.models.user import User

app = create_app('development')

with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='super_admin').first():
        u = User(username='superadmin', email='admin@ctms.com', role='super_admin')
        u.set_password('Admin@1234')
        db.session.add(u)
        db.session.commit()
        print('Super Admin created — username: superadmin  password: Admin@1234')
        print('Change this password immediately after first login!')
    else:
        print('Super Admin already exists.')
