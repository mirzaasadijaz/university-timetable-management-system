from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from app import db
from app.models.course     import Course
from app.models.department import Department
from app.utils.decorators  import role_required

courses_bp = Blueprint('courses', __name__)

class CourseForm(FlaskForm):
    code          = StringField('Code', validators=[DataRequired(), Length(max=20)])
    title         = StringField('Title', validators=[DataRequired(), Length(max=120)])
    credit_hours  = IntegerField('Credit Hours', validators=[NumberRange(1,6)], default=3)
    course_type   = SelectField('Type', choices=[
        ('theory','Theory'),('lab','Lab'),('seminar','Seminar')])
    department_id = SelectField('Department', coerce=int)
    submit        = SubmitField('Save')
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.department_id.choices = [(0,'-- None --')] + [
            (d.id,d.name) for d in Department.query.order_by('name').all()]

@courses_bp.route('/')
@login_required
@role_required('super_admin','admin','manager')
def list_courses():
    search = request.args.get('search','')
    page   = request.args.get('page',1,type=int)
    q = Course.query
    if search: q = q.filter(Course.title.ilike(f'%{search}%')|Course.code.ilike(f'%{search}%'))
    courses = q.order_by(Course.code).paginate(page=page,per_page=20)
    return render_template('courses/list.html',courses=courses,search=search)

@courses_bp.route('/add', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def add_course():
    form = CourseForm()
    if form.validate_on_submit():
        if Course.query.filter_by(code=form.code.data).first():
            flash('Course code already exists.','danger')
            return render_template('courses/form.html',form=form,title='Add Course')
        c = Course(code=form.code.data, title=form.title.data,
                   credit_hours=form.credit_hours.data, course_type=form.course_type.data,
                   department_id=form.department_id.data or None)
        db.session.add(c); db.session.commit()
        flash(f'Course {c.code} added.','success')
        return redirect(url_for('courses.list_courses'))
    return render_template('courses/form.html',form=form,title='Add Course')

@courses_bp.route('/<int:id>/edit', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def edit_course(id):
    c = Course.query.get_or_404(id)
    form = CourseForm(obj=c)
    if form.validate_on_submit():
        c.code=form.code.data; c.title=form.title.data
        c.credit_hours=form.credit_hours.data; c.course_type=form.course_type.data
        c.department_id=form.department_id.data or None
        db.session.commit(); flash('Course updated.','success')
        return redirect(url_for('courses.list_courses'))
    return render_template('courses/form.html',form=form,title='Edit Course')

@courses_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('super_admin')
def delete_course(id):
    c = Course.query.get_or_404(id)
    if c.schedule_entries:
        flash('Cannot delete: course has schedule entries.','danger')
        return redirect(url_for('courses.list_courses'))
    db.session.delete(c); db.session.commit()
    flash('Course deleted.','info')
    return redirect(url_for('courses.list_courses'))
