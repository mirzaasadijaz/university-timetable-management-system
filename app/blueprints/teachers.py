from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from app import db
from app.models.teacher    import Teacher
from app.models.department import Department
from app.models.user       import User  # <-- ADDED IMPORT
from app.utils.decorators  import role_required

teachers_bp = Blueprint('teachers', __name__)

class TeacherForm(FlaskForm):
    full_name     = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    employee_code = StringField('Employee Code', validators=[DataRequired(), Length(max=20)])
    
    # <-- ADDED: Dropdown to select the linked user account
    user_id       = SelectField('Linked User Account', coerce=int) 
    
    designation   = SelectField('Designation', choices=[
        ('Lecturer','Lecturer'),('Senior Lecturer','Senior Lecturer'),
        ('Assistant Professor','Assistant Professor'),
        ('Associate Professor','Associate Professor'),('Professor','Professor')])
    department_id = SelectField('Department', coerce=int)
    contact       = StringField('Contact', validators=[Optional(), Length(max=20)])
    submit        = SubmitField('Save')
    
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        self.department_id.choices = [(0,'-- None --')] + [
            (d.id,d.name) for d in Department.query.order_by('name').all()]
        
        # <-- ADDED: Populate the user dropdown
        self.user_id.choices = [(u.id, u.username) for u in User.query.order_by('username').all()]

@teachers_bp.route('/')
@login_required
@role_required('super_admin','admin','manager')
def list_teachers():
    search = request.args.get('search','')
    page   = request.args.get('page',1,type=int)
    q = Teacher.query
    if search: q = q.filter(Teacher.full_name.ilike(f'%{search}%'))
    teachers = q.order_by(Teacher.full_name).paginate(page=page,per_page=20)
    return render_template('teachers/list.html', teachers=teachers, search=search)

@teachers_bp.route('/add', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def add_teacher():
    form = TeacherForm()
    if form.validate_on_submit():
        if Teacher.query.filter_by(employee_code=form.employee_code.data).first():
            flash('Employee code already exists.','danger')
            return render_template('teachers/form.html',form=form,title='Add Teacher')
        
        t = Teacher(full_name=form.full_name.data,
                    employee_code=form.employee_code.data,
                    designation=form.designation.data,
                    department_id=form.department_id.data or None,
                    contact=form.contact.data,
                    user_id=form.user_id.data)  # <-- ADDED: Save the user_id
        
        db.session.add(t); db.session.commit()
        flash(f'Teacher {t.full_name} added.','success')
        return redirect(url_for('teachers.list_teachers'))
    return render_template('teachers/form.html',form=form,title='Add Teacher')

@teachers_bp.route('/<int:id>/edit', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def edit_teacher(id):
    t = Teacher.query.get_or_404(id)
    form = TeacherForm(obj=t)
    if form.validate_on_submit():
        t.full_name=form.full_name.data; t.employee_code=form.employee_code.data
        t.designation=form.designation.data; t.contact=form.contact.data
        t.department_id=form.department_id.data or None
        t.user_id=form.user_id.data  # <-- ADDED: Update the user_id
        
        db.session.commit()
        flash('Teacher updated.','success')
        return redirect(url_for('teachers.list_teachers'))
    return render_template('teachers/form.html',form=form,title='Edit Teacher')

@teachers_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('super_admin')
def delete_teacher(id):
    t = Teacher.query.get_or_404(id)
    if t.schedules.count():
        flash('Cannot delete: teacher has schedule entries.','danger')
        return redirect(url_for('teachers.list_teachers'))
    db.session.delete(t); db.session.commit()
    flash('Teacher deleted.','info')
    return redirect(url_for('teachers.list_teachers'))