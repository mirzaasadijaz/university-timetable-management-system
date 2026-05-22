from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from app import db
from app.models.department import Department
from app.utils.decorators  import role_required

departments_bp = Blueprint('departments', __name__)

class DeptForm(FlaskForm):
    name   = StringField('Department Name', validators=[DataRequired(), Length(max=100)])
    code   = StringField('Short Code',      validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Save')

@departments_bp.route('/')
@login_required
@role_required('super_admin','admin','manager')
def list_departments():
    depts = Department.query.order_by(Department.name).all()
    return render_template('departments/list.html', depts=depts)

@departments_bp.route('/add', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def add_department():
    form = DeptForm()
    if form.validate_on_submit():
        if Department.query.filter_by(code=form.code.data.upper()).first():
            flash('Department code already exists.','danger')
            return render_template('departments/form.html',form=form,title='Add Department')
        d = Department(name=form.name.data, code=form.code.data.upper())
        db.session.add(d); db.session.commit()
        flash(f'Department {d.name} added.','success')
        return redirect(url_for('departments.list_departments'))
    return render_template('departments/form.html', form=form, title='Add Department')

@departments_bp.route('/<int:id>/edit', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def edit_department(id):
    d = Department.query.get_or_404(id)
    form = DeptForm(obj=d)
    if form.validate_on_submit():
        d.name = form.name.data
        d.code = form.code.data.upper()
        db.session.commit()
        flash('Department updated.','success')
        return redirect(url_for('departments.list_departments'))
    return render_template('departments/form.html', form=form, title='Edit Department')

@departments_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('super_admin')
def delete_department(id):
    d = Department.query.get_or_404(id)
    if d.teachers.count() or d.courses.count():
        flash('Cannot delete: department has teachers or courses assigned.','danger')
        return redirect(url_for('departments.list_departments'))
    db.session.delete(d); db.session.commit()
    flash('Department deleted.','info')
    return redirect(url_for('departments.list_departments'))
