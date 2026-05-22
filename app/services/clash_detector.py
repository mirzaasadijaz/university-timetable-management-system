from app.models.schedule import ClassTimeSchedule

class ClashDetector:

    @staticmethod
    def _base(teacher_id, room_id, section_id, time_slot_id, exclude_id=None):
        """Build base queries for all three clash types."""
        def q(filters):
            qry = ClassTimeSchedule.query.filter_by(**filters)
            if exclude_id:
                qry = qry.filter(ClassTimeSchedule.id != exclude_id)
            return qry.first()
        return (
            q({'teacher_id': teacher_id,  'time_slot_id': time_slot_id}),
            q({'room_id':    room_id,      'time_slot_id': time_slot_id}),
            q({'section_id': section_id,   'time_slot_id': time_slot_id}),
        )

    @staticmethod
    def check_all(teacher_id, room_id, section_id, time_slot_id, exclude_id=None):
        """Return dict of clash messages. Empty dict = all clear."""
        tc, rc, sc = ClashDetector._base(
            teacher_id, room_id, section_id, time_slot_id, exclude_id)
        errors = {}
        if tc:
            errors['teacher'] = (f'Teacher already scheduled for "{tc.course.title}"'
                                 f' in Room {tc.room.room_number} at this time.')
        if rc:
            errors['room'] = (f'Room already booked for "{rc.course.title}"'
                              f' (Section {rc.section.name}) at this time.')
        if sc:
            errors['section'] = (f'Section already has "{sc.course.title}"'
                                 f' at this time slot.')
        return errors

    @staticmethod
    def get_all_clashes():
        """Scan full schedule and return all clash pairs grouped by type."""
        entries = ClassTimeSchedule.query.all()
        seen_t, seen_r, seen_s = {}, {}, {}
        clashes = {'teacher': [], 'room': [], 'section': []}
        for e in entries:
            tk = (e.teacher_id, e.time_slot_id)
            rk = (e.room_id,    e.time_slot_id)
            sk = (e.section_id, e.time_slot_id)
            if tk in seen_t: clashes['teacher'].append((seen_t[tk], e))
            else: seen_t[tk] = e
            if rk in seen_r: clashes['room'].append((seen_r[rk], e))
            else: seen_r[rk] = e
            if sk in seen_s: clashes['section'].append((seen_s[sk], e))
            else: seen_s[sk] = e
        return clashes
