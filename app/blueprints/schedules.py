from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from app import db
from app.models.schedule  import ClassTimeSchedule
from app.models.teacher   import Teacher
from app.models.course    import Course
from app.models.room      import Room
from app.models.timeslot  import TimeSlot
from app.models.section   import Section
from app.services.clash_detector import ClashDetector
from app.utils.decorators import role_required

schedules_bp = Blueprint('schedules', __name__)

class ScheduleForm(FlaskForm):
    teacher_id      = SelectField('Teacher',   coerce=int, validators=[DataRequired()])
    course_id       = SelectField('Course',    coerce=int, validators=[DataRequired()])
    
    building        = SelectField('Building') 
    room_id         = SelectField('Room',      coerce=int, validators=[DataRequired()])
    
    semester_filter = SelectField('Semester',  coerce=int, choices=[
        (1,'1st Sem'), (2,'2nd Sem'), (3,'3rd Sem'), (4,'4th Sem'), 
        (5,'5th Sem'), (6,'6th Sem'), (7,'7th Sem'), (8,'8th Sem')
    ])
    section_id      = SelectField('Section',   coerce=int, validators=[DataRequired()])
    
    day             = SelectField('Day', choices=[('Monday','Monday'), ('Tuesday','Tuesday'), ('Wednesday','Wednesday'), ('Thursday','Thursday'), ('Friday','Friday'), ('Saturday','Saturday')])
    time_slot_id    = SelectField('Time Slot', coerce=int, validators=[DataRequired()])
    
    submit          = SubmitField('Check & Save')
    
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.teacher_id.choices  = [(t.id,t.full_name) for t in Teacher.query.order_by('full_name').all()]
        self.course_id.choices   = [(c.id,f'{c.code} – {c.title}') for c in Course.query.order_by('code').all()]
        
        rooms = Room.query.order_by('building').all()
        unique_buildings = list(set([r.building for r in rooms]))
        self.building.choices = [(b, b) for b in unique_buildings]
        
        self.room_id.choices = [(r.id, f"{r.building}|{r.room_type} {r.room_number}{f' - {r.floor.title()} Floor' if r.floor else ''}") for r in rooms]

        self.section_id.choices  = [(s.id, f"{s.semester}|{s.program} - {s.name}") for s in Section.query.order_by('name').all()]
        
        self.time_slot_id.choices= [(s.id, f"{s.day}|{s.start_time} - {s.end_time}") for s in TimeSlot.query.order_by('day','start_time').all()]

@schedules_bp.route('/')
@login_required
@role_required('super_admin','admin','manager')
def list_schedules():
    # NAYA: DAYS ko import karein
    from app.models.timeslot import DAYS 
    page = request.args.get('page', 1, type=int)
    
    # 1. URL se filters get karein
    semester_val = request.args.get('semester', type=int)
    tf = request.args.get('teacher_id', type=int)
    sf = request.args.get('section_id', type=int)
    
    # NAYA: Day aur Time alag alag get karein
    day_val = request.args.get('day', type=str)
    time_val = request.args.get('time', type=str)  
    
    # 2. Main Query banayen
    q = ClassTimeSchedule.query
    
    if semester_val:
        q = q.join(Section).filter(Section.semester == semester_val)
    if sf:
        q = q.filter(ClassTimeSchedule.section_id == sf)
    if tf:
        q = q.filter(ClassTimeSchedule.teacher_id == tf)
        
    # NAYA: Day aur Time ka filter lagayen
    if day_val or time_val:
        q = q.join(TimeSlot)
        if day_val:
            q = q.filter(TimeSlot.day == day_val)
        if time_val:
            all_s = TimeSlot.query.all()
            valid_slot_ids = [s.id for s in all_s if f"{s.start_time}-{s.end_time}" == time_val]
            q = q.filter(ClassTimeSchedule.time_slot_id.in_(valid_slot_ids))
            
    schedules = q.paginate(page=page, per_page=30)
    
    # 3. SMART BACKEND FILTERING FOR DROPDOWNS
    # A. Semesters
    sem_q = db.session.query(Section.semester).distinct()
    if tf:
        sem_q = sem_q.join(ClassTimeSchedule, ClassTimeSchedule.section_id == Section.id)\
                     .filter(ClassTimeSchedule.teacher_id == tf)
    semesters = [s[0] for s in sem_q.order_by(Section.semester).all()]

    # B. Sections
    sec_q = Section.query
    if semester_val:
        sec_q = sec_q.filter(Section.semester == semester_val)
    if tf:
        sec_q = sec_q.join(ClassTimeSchedule).filter(ClassTimeSchedule.teacher_id == tf).distinct()
    sections = sec_q.order_by(Section.program, Section.name).all()

    # C. Teachers
    tea_q = Teacher.query
    if semester_val or sf:
        tea_q = tea_q.join(ClassTimeSchedule)
        if sf:
            tea_q = tea_q.filter(ClassTimeSchedule.section_id == sf)
        elif semester_val:
            tea_q = tea_q.join(Section, ClassTimeSchedule.section_id == Section.id)\
                         .filter(Section.semester == semester_val)
        tea_q = tea_q.distinct()
    teachers = tea_q.order_by(Teacher.full_name).all()

    # D. NAYA: Dropdown ke liye alag alag Days aur Times
    days_list = DAYS[:6] # Mon - Sat
    
    all_slots = TimeSlot.query.order_by(TimeSlot.start_time).all()
    unique_times = []
    seen_t = set()
    for s in all_slots:
        tk = f"{s.start_time}-{s.end_time}"
        if tk not in seen_t:
            unique_times.append({'start_time': s.start_time, 'end_time': s.end_time, 'key': tk})
            seen_t.add(tk)

    return render_template('schedules/list.html',
        schedules=schedules, teachers=teachers, sections=sections, semesters=semesters,
        days_list=days_list, unique_times=unique_times, # NAYA
        tf=tf, sf=sf, semester_val=semester_val,
        day_val=day_val, time_val=time_val) # NAYA

@schedules_bp.route('/add', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def add_schedule():
    form = ScheduleForm()
    clashes = {}
    if form.validate_on_submit():
        clashes = ClashDetector.check_all(
            teacher_id=form.teacher_id.data, room_id=form.room_id.data,
            section_id=form.section_id.data, time_slot_id=form.time_slot_id.data)
        
        if clashes:
            for k,msg in clashes.items():
                flash(f'[{k.upper()} CLASH] {msg}','danger')
        else:
            selected_section = Section.query.get(form.section_id.data)
            
            s = ClassTimeSchedule(
                teacher_id=form.teacher_id.data, course_id=form.course_id.data,
                room_id=form.room_id.data, time_slot_id=form.time_slot_id.data,
                section_id=form.section_id.data,
                
                semester_label=f"{selected_section.semester} Semester", 
                
                created_by=current_user.id)
            db.session.add(s); db.session.commit()
            flash('Schedule entry added successfully!','success')
            return redirect(url_for('schedules.list_schedules'))
    return render_template('schedules/form.html',form=form,title='Add Schedule',clashes=clashes)

@schedules_bp.route('/<int:id>/edit', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def edit_schedule(id):
    s = ClassTimeSchedule.query.get_or_404(id)
    form = ScheduleForm(obj=s)
    
    if request.method == 'GET':
        form.day.data = s.time_slot.day
        form.semester_filter.data = s.section.semester
        form.building.data = s.room.building
        
    clashes = {}
    if form.validate_on_submit():
        clashes = ClashDetector.check_all(
            teacher_id=form.teacher_id.data, room_id=form.room_id.data,
            section_id=form.section_id.data, time_slot_id=form.time_slot_id.data,
            exclude_id=s.id)
        
        if clashes:
            for k,msg in clashes.items(): flash(f'[{k.upper()} CLASH] {msg}','danger')
        else:
            # AUTO-FILL LOGIC FOR EDIT: 
            selected_section = Section.query.get(form.section_id.data)

            s.teacher_id=form.teacher_id.data; s.course_id=form.course_id.data
            s.room_id=form.room_id.data; s.time_slot_id=form.time_slot_id.data
            s.section_id=form.section_id.data
            
            s.semester_label=f"{selected_section.semester} Semester" 
            
            db.session.commit(); flash('Schedule updated.','success')
            return redirect(url_for('schedules.list_schedules'))
    return render_template('schedules/form.html',form=form,title='Edit Schedule',clashes=clashes)

@schedules_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('super_admin','admin')
def delete_schedule(id):
    s = ClassTimeSchedule.query.get_or_404(id)
    db.session.delete(s); db.session.commit()
    flash('Entry deleted.','info')
    return redirect(url_for('schedules.list_schedules'))

@schedules_bp.route('/<int:id>/publish', methods=['POST'])
@login_required
@role_required('super_admin','admin')
def publish_schedule(id):
    s = ClassTimeSchedule.query.get_or_404(id)
    s.status = 'published'; db.session.commit()
    flash('Entry published.','success')
    return redirect(url_for('schedules.list_schedules'))

@schedules_bp.route('/timetable')
@login_required
def timetable_grid():
    """Visual weekly timetable grid."""
    from app.models.timeslot import DAYS
    
    semester_val = request.args.get('semester', type=int)
    section_id   = request.args.get('section_id', type=int)
    teacher_id   = request.args.get('teacher_id', type=int)
    
    time_filter  = request.args.get('time_filter', type=str) 
    
    logged_in_teacher = None
    if current_user.role == 'teacher':
        logged_in_teacher = Teacher.query.filter_by(user_id=current_user.id).first()
        if logged_in_teacher:
            teacher_id = logged_in_teacher.id 

    q = ClassTimeSchedule.query.filter(ClassTimeSchedule.status == 'published')
    
    if semester_val: 
        q = q.join(Section).filter(Section.semester == semester_val)
    if section_id: 
        q = q.filter(ClassTimeSchedule.section_id == section_id)
    if teacher_id: 
        q = q.filter(ClassTimeSchedule.teacher_id == teacher_id)
    
    slots = TimeSlot.query.order_by(TimeSlot.start_time).all()
    days  = DAYS[:6]   # Mon–Sat
    
    # Dropdown ke liye tamam unique times nikalein
    all_time_periods = []
    seen_times = set()
    for slot in slots:
        time_key = f"{slot.start_time}-{slot.end_time}"
        if time_key not in seen_times:
            all_time_periods.append({
                'start_time': slot.start_time, 
                'end_time': slot.end_time, 
                'key': time_key
            })
            seen_times.add(time_key)

    # 2. TIME FILTER APPLY KAREIN
    if time_filter:
        valid_slot_ids = [s.id for s in slots if f"{s.start_time}-{s.end_time}" == time_filter]
        q = q.filter(ClassTimeSchedule.time_slot_id.in_(valid_slot_ids))
        # Grid mein sirf wahi row show ho jo select hui hai
        unique_time_periods = [tp for tp in all_time_periods if tp['key'] == time_filter]
    else:
        unique_time_periods = all_time_periods

    entries = q.all()

    grid = {day: {tp['key']: [] for tp in unique_time_periods} for day in days}
    
    for e in entries:
        if e.time_slot and e.time_slot.day in grid:
            time_key = f"{e.time_slot.start_time}-{e.time_slot.end_time}"
            if time_key in grid[e.time_slot.day]:
                grid[e.time_slot.day][time_key].append(e)
                
    sem_q = db.session.query(Section.semester).distinct()
    if teacher_id:
        sem_q = sem_q.join(ClassTimeSchedule, ClassTimeSchedule.section_id == Section.id)\
                     .filter(ClassTimeSchedule.teacher_id == teacher_id, ClassTimeSchedule.status == 'published')
    semesters = [s[0] for s in sem_q.order_by(Section.semester).all()]

    sec_q = Section.query
    if semester_val:
        sec_q = sec_q.filter(Section.semester == semester_val)
    if teacher_id:
        sec_q = sec_q.join(ClassTimeSchedule).filter(
            ClassTimeSchedule.teacher_id == teacher_id, 
            ClassTimeSchedule.status == 'published'
        ).distinct()
    sections = sec_q.order_by(Section.program, Section.name).all()

    tea_q = Teacher.query
    if current_user.role == 'teacher' and logged_in_teacher:
        tea_q = tea_q.filter(Teacher.id == logged_in_teacher.id)
    else:
        if semester_val or section_id:
            tea_q = tea_q.join(ClassTimeSchedule).filter(ClassTimeSchedule.status == 'published')
            if section_id:
                tea_q = tea_q.filter(ClassTimeSchedule.section_id == section_id)
            elif semester_val:
                tea_q = tea_q.join(Section, ClassTimeSchedule.section_id == Section.id)\
                             .filter(Section.semester == semester_val)
            tea_q = tea_q.distinct()
            
    teachers = tea_q.order_by(Teacher.full_name).all()
    
    return render_template('schedules/timetable.html',
        grid=grid, days=days, unique_time_periods=unique_time_periods, 
        all_time_periods=all_time_periods, slots=slots, # NAYA: all_time_periods pass kiya hai
        sections=sections, teachers=teachers, semesters=semesters,
        sel_section=section_id, sel_teacher=teacher_id, sel_semester=semester_val,
        sel_time=time_filter) # NAYA: selected time