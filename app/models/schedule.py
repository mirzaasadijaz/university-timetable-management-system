from app import db
from datetime import datetime

class ClassTimeSchedule(db.Model):
    __tablename__  = 'class_time_schedule'
    id             = db.Column(db.Integer, primary_key=True)
    teacher_id     = db.Column(db.Integer, db.ForeignKey('teachers.id'),   nullable=False)
    course_id      = db.Column(db.Integer, db.ForeignKey('courses.id'),    nullable=False)
    room_id        = db.Column(db.Integer, db.ForeignKey('rooms.id'),      nullable=False)
    time_slot_id   = db.Column(db.Integer, db.ForeignKey('time_slots.id'), nullable=False)
    section_id     = db.Column(db.Integer, db.ForeignKey('sections.id'),   nullable=False)
    semester_label = db.Column(db.String(20), nullable=False, default='Fall-2025')
    status         = db.Column(db.String(15), nullable=False, default='draft')
    # status: 'draft', 'published', 'archived'
    created_by     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    course    = db.relationship('Course',   backref='schedule_entries')
    room      = db.relationship('Room',     backref='schedule_entries')
    time_slot = db.relationship('TimeSlot', backref='schedule_entries')
    creator   = db.relationship('User',     foreign_keys=[created_by])

    # Indexes speed up clash detection queries
    __table_args__ = (
        db.Index('ix_cts_teacher_slot',  'teacher_id',  'time_slot_id'),
        db.Index('ix_cts_room_slot',     'room_id',     'time_slot_id'),
        db.Index('ix_cts_section_slot',  'section_id',  'time_slot_id'),
    )

    def __repr__(self):
        return f'<Schedule id={self.id} status={self.status}>'
