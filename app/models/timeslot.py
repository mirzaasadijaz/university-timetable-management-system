from app import db

DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

class TimeSlot(db.Model):
    __tablename__ = 'time_slots'
    id         = db.Column(db.Integer, primary_key=True)
    day        = db.Column(db.String(15), nullable=False)
    start_time = db.Column(db.String(8),  nullable=False)  # 'HH:MM'
    end_time   = db.Column(db.String(8),  nullable=False)  # 'HH:MM'
    label      = db.Column(db.String(50), nullable=True)

    __table_args__ = (db.UniqueConstraint('day','start_time','end_time'),)

    @property
    def display(self): return f'{self.day}  {self.start_time}–{self.end_time}'

    def __repr__(self): return f'<TimeSlot {self.display}>'
