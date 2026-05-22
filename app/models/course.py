from app import db

# Many-to-Many junction: Section <-> Course
section_courses = db.Table('section_courses',
    db.Column('section_id', db.Integer, db.ForeignKey('sections.id'), primary_key=True),
    db.Column('course_id',  db.Integer, db.ForeignKey('courses.id'),  primary_key=True)
)

class Course(db.Model):
    __tablename__  = 'courses'
    id             = db.Column(db.Integer, primary_key=True)
    code           = db.Column(db.String(20),  unique=True, nullable=False)
    title          = db.Column(db.String(120), nullable=False)
    credit_hours   = db.Column(db.Integer, nullable=False, default=3)
    course_type    = db.Column(db.String(20), nullable=False, default='theory')
    # course_type values: 'theory', 'lab', 'seminar'
    department_id  = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)

    def __repr__(self): return f'<Course {self.code}: {self.title}>'
