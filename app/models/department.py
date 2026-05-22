from app import db

class Department(db.Model):
    __tablename__ = 'departments'
    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20),  unique=True, nullable=False)

    teachers = db.relationship('Teacher', backref='department', lazy='dynamic')
    courses  = db.relationship('Course',  backref='department', lazy='dynamic')

    def __repr__(self): return f'<Department {self.name}>'
