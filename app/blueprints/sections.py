from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
# ADDED SelectField here
from wtforms import StringField, IntegerField, SubmitField, SelectField 
from wtforms.validators import DataRequired, Length, NumberRange
from app import db
from app.models.section   import Section
from app.utils.decorators import role_required

sections_bp = Blueprint('sections', __name__)

class SectionForm(FlaskForm):
    name     = StringField('Section Name', validators=[DataRequired(), Length(max=50)])
    program  = StringField('Program',      validators=[DataRequired(), Length(max=80)])
    
    # NAYA SEMESTER FIELD: Ab yeh user ko '1st Semester' dikhayega, lekin DB mein '1' save karega
    semester = SelectField('Semester', coerce=int, choices=[
        (1, '1st Semester'), (2, '2nd Semester'), (3, '3rd Semester'),
        (4, '4th Semester'), (5, '5th Semester'), (6, '6th Semester'),
        (7, '7th Semester'), (8, '8th Semester'), (9, '9th Semester'),
        (10, '10th Semester'), (11, '11th Semester'), (12, '12th Semester')
    ], default=1)
    
    strength = IntegerField('Strength',    validators=[NumberRange(0,500)], default=0)
    submit   = SubmitField('Save')

@sections_bp.route('/')
@login_required
@role_required('super_admin','admin','manager')
def list_sections():
    search = request.args.get('search','')
    page   = request.args.get('page',1,type=int)
    q = Section.query
    if search: q = q.filter(Section.name.ilike(f'%{search}%')|Section.program.ilike(f'%{search}%'))
    sections = q.order_by(Section.program,Section.semester).paginate(page=page,per_page=20)
    return render_template('sections/list.html',sections=sections,search=search)

@sections_bp.route('/add', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def add_section():
    form = SectionForm()
    if form.validate_on_submit():
        # CHECK: Duplicate Section rokne ke liye
        existing_section = Section.query.filter_by(
            name=form.name.data, 
            program=form.program.data, 
            semester=form.semester.data
        ).first()
        
        if existing_section:
            flash(f'Section {form.name.data} already exists for {form.program.data} Semester {form.semester.data}.', 'danger')
            return render_template('sections/form.html', form=form, title='Add Section')

        s = Section(name=form.name.data, program=form.program.data,
                    semester=form.semester.data, strength=form.strength.data)
        db.session.add(s); db.session.commit()
        flash(f'Section {s.name} added.','success')
        return redirect(url_for('sections.list_sections'))
    return render_template('sections/form.html',form=form,title='Add Section')

@sections_bp.route('/<int:id>/edit', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def edit_section(id):
    s = Section.query.get_or_404(id)
    form = SectionForm(obj=s)
    if form.validate_on_submit():
        # CHECK: Edit karte waqt duplicate rokne ke liye
        existing_section = Section.query.filter_by(
            name=form.name.data, 
            program=form.program.data, 
            semester=form.semester.data
        ).first()
        
        if existing_section and existing_section.id != s.id:
            flash(f'Section {form.name.data} already exists for {form.program.data} Semester {form.semester.data}.', 'danger')
            return render_template('sections/form.html', form=form, title='Edit Section')

        s.name=form.name.data; s.program=form.program.data
        s.semester=form.semester.data; s.strength=form.strength.data
        db.session.commit(); flash('Section updated.','success')
        return redirect(url_for('sections.list_sections'))
    return render_template('sections/form.html',form=form,title='Edit Section')

@sections_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('super_admin')
def delete_section(id):
    s = Section.query.get_or_404(id)
    if s.schedules.count():
        flash('Cannot delete: section has schedule entries.','danger')
        return redirect(url_for('sections.list_sections'))
    db.session.delete(s); db.session.commit()
    flash('Section deleted.','info')
    return redirect(url_for('sections.list_sections'))