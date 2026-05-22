from app import db

class Room(db.Model):
    __tablename__  = 'rooms'
    id             = db.Column(db.Integer, primary_key=True)
    room_number    = db.Column(db.String(20),  nullable=False)
    floor          = db.Column(db.String(20))
    building       = db.Column(db.String(80))
    capacity       = db.Column(db.Integer,     nullable=False, default=40)
    room_type      = db.Column(db.String(20),  nullable=False, default='classroom')
    # room_type: 'classroom', 'lab', 'seminar', 'auditorium'
    is_available   = db.Column(db.Boolean, default=True)

    def is_free_at(self, time_slot_id, exclude_id=None):
        from app.models.schedule import ClassTimeSchedule
        q = ClassTimeSchedule.query.filter_by(room_id=self.id, time_slot_id=time_slot_id)
        if exclude_id: q = q.filter(ClassTimeSchedule.id != exclude_id)
        return q.first() is None

    def __repr__(self): return f'<Room {self.room_number} ({self.building})>'
