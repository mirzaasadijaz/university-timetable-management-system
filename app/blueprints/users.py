from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional
from app import db
from app.models.user import User
from app.utils.decorators import role_required
from app.utils.helpers import get_creatable_roles

users_bp = Blueprint('users', __name__)

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3,80)])
    email    = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Optional(), Length(min=8)])
    role     = SelectField('Role', choices=[])
    is_active= BooleanField('Active', default=True)
    submit   = SubmitField('Save User')

@users_bp.route('/')
@login_required
@role_required('super_admin','admin')
def list_users():
    search = request.args.get('search','')
    page   = request.args.get('page',1,type=int)
    q = User.query
    if search: q = q.filter(User.username.ilike(f'%{search}%'))
    users = q.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    return render_template('users/list.html', users=users, search=search)

@users_bp.route('/add', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def add_user():
    form = UserForm()
    allowed = get_creatable_roles(current_user.role)
    form.role.choices = [(r,r.replace('_',' ').title()) for r in allowed]
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.','danger')
            return render_template('users/form.html', form=form, title='Add User')
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.','danger')
            return render_template('users/form.html', form=form, title='Add User')
        u = User(username=form.username.data, email=form.email.data,
                 role=form.role.data, is_active=form.is_active.data,
                 created_by=current_user.id)
        u.set_password(form.password.data)
        db.session.add(u); db.session.commit()
        flash(f'User {u.username} created.','success')
        return redirect(url_for('users.list_users'))
    return render_template('users/form.html', form=form, title='Add User')

@users_bp.route('/<int:id>/edit', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def edit_user(id):
    u = User.query.get_or_404(id)
    form = UserForm(obj=u)
    allowed = get_creatable_roles(current_user.role)
    form.role.choices = [(r,r.replace('_',' ').title()) for r in allowed]
    if form.validate_on_submit():
        u.username  = form.username.data
        u.email     = form.email.data
        u.role      = form.role.data
        u.is_active = form.is_active.data
        if form.password.data: u.set_password(form.password.data)
        db.session.commit()
        flash('User updated.','success')
        return redirect(url_for('users.list_users'))
    return render_template('users/form.html', form=form, title='Edit User')

@users_bp.route('/<int:id>/toggle', methods=['POST'])
@login_required
@role_required('super_admin','admin')
def toggle_user(id):
    u = User.query.get_or_404(id)
    u.is_active = not u.is_active
    db.session.commit()
    state = 'activated' if u.is_active else 'deactivated'
    flash(f'User {u.username} {state}.','info')
    return redirect(url_for('users.list_users'))

@users_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('super_admin')
def delete_user(id):
    u = User.query.get_or_404(id)
    if u.id == current_user.id:
        flash('Cannot delete your own account.','danger')
        return redirect(url_for('users.list_users'))
    db.session.delete(u); db.session.commit()
    flash('User deleted.','info')
    return redirect(url_for('users.list_users'))
