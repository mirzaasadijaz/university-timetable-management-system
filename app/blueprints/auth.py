from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from app.models.user import User

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3,80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit   = SubmitField('Login')

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))
        if not user.is_active:
            flash('Account is deactivated. Contact administrator.', 'warning')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember.data)
        flash(f'Welcome back, {user.username}!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('dashboard.index'))
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET','POST'])
@login_required
def change_password():
    from flask_wtf import FlaskForm
    from wtforms import PasswordField, SubmitField
    from wtforms.validators import DataRequired, EqualTo, Length
    class CPForm(FlaskForm):
        current  = PasswordField('Current Password', validators=[DataRequired()])
        new_pw   = PasswordField('New Password', validators=[DataRequired(), Length(8)])
        confirm  = PasswordField('Confirm', validators=[EqualTo('new_pw')])
        submit   = SubmitField('Update Password')
    form = CPForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current.data):
            flash('Current password is incorrect.', 'danger')
        else:
            current_user.set_password(form.new_pw.data)
            from app import db; db.session.commit()
            flash('Password updated successfully.', 'success')
            return redirect(url_for('dashboard.index'))
    return render_template('auth/change_password.html', form=form)
