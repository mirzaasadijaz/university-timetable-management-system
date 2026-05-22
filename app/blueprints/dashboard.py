from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.teacher  import Teacher
from app.models.room     import Room
from app.models.course   import Course
from app.models.section  import Section
from app.models.schedule import ClassTimeSchedule
from app.services.clash_detector import ClashDetector

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    role = current_user.role
    clashes = ClashDetector.get_all_clashes()
    clash_count = sum(len(v) for v in clashes.values())
    stats = {
        'teachers':  Teacher.query.count(), 
        'rooms':     Room.query.count(),
        'courses':   Course.query.count(),
        'sections':  Section.query.count(),
        'schedules': ClassTimeSchedule.query.count(),
        'clashes':   clash_count,
    }
    recent = []
    teacher_profile = None
    my_schedule = []
    if role in ('super_admin','admin','manager'):
        recent = (ClassTimeSchedule.query
                  .order_by(ClassTimeSchedule.created_at.desc()).limit(5).all())
    if role == 'teacher':
        teacher_profile = Teacher.query.filter_by(user_id=current_user.id).first()
        if teacher_profile:
            my_schedule = teacher_profile.schedules.all()
    return render_template('dashboard/index.html',
        stats=stats, recent=recent,
        my_schedule=my_schedule, clash_count=clash_count)
