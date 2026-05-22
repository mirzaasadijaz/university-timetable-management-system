from app import db

# Many-to-Many junction: Teacher <-> Course
teacher_courses = db.Table('teacher_courses',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id'), primary_key=True),
    db.Column('course_id',  db.Integer, db.ForeignKey('courses.id'),  primary_key=True)
)

class Teacher(db.Model):
    __tablename__  = 'teachers'
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    full_name      = db.Column(db.String(120), nullable=False)
    employee_code  = db.Column(db.String(20), unique=True, nullable=False)
    department_id  = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    designation    = db.Column(db.String(80), nullable=False, default='Lecturer')
    contact        = db.Column(db.String(20), nullable=True)

    user      = db.relationship('User', backref=db.backref('teacher_profile', uselist=False))
    courses   = db.relationship('Course', secondary=teacher_courses,
                   backref=db.backref('teachers', lazy='dynamic'))
    schedules = db.relationship('ClassTimeSchedule', backref='teacher', lazy='dynamic')

    def get_weekly_hours(self): return self.schedules.count()
    def __repr__(self): return f'<Teacher {self.full_name}>'
