from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from app import db
from app.models.timeslot  import TimeSlot, DAYS
from app.utils.decorators import role_required

timeslots_bp = Blueprint('timeslots', __name__)

class SlotForm(FlaskForm):
    day        = SelectField('Day', choices=[(d,d) for d in DAYS])
    start_time = StringField('Start (HH:MM)', validators=[DataRequired(), Length(5,5)])
    end_time   = StringField('End   (HH:MM)', validators=[DataRequired(), Length(5,5)])
    label      = StringField('Label', validators=[Length(max=50)])
    submit     = SubmitField('Save')

@timeslots_bp.route('/')
@login_required
def list_slots():
    slots = TimeSlot.query.order_by(TimeSlot.day, TimeSlot.start_time).all()
    return render_template('timeslots/list.html', slots=slots)

@timeslots_bp.route('/add', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def add_slot():
    form = SlotForm()
    if form.validate_on_submit():
        s = TimeSlot(day=form.day.data, start_time=form.start_time.data,
                     end_time=form.end_time.data, label=form.label.data)
        db.session.add(s); db.session.commit()
        flash('Time slot added.','success')
        return redirect(url_for('timeslots.list_slots'))
    return render_template('timeslots/form.html',form=form,title='Add Time Slot')

@timeslots_bp.route('/<int:id>/edit', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def edit_slot(id):
    s = TimeSlot.query.get_or_404(id)
    form = SlotForm(obj=s)
    if form.validate_on_submit():
        s.day=form.day.data; s.start_time=form.start_time.data
        s.end_time=form.end_time.data; s.label=form.label.data
        db.session.commit(); flash('Slot updated.','success')
        return redirect(url_for('timeslots.list_slots'))
    return render_template('timeslots/form.html',form=form,title='Edit Slot')

@timeslots_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('super_admin')
def delete_slot(id):
    s = TimeSlot.query.get_or_404(id)
    if s.schedule_entries:
        flash('Cannot delete: slot used in schedule.','danger')
        return redirect(url_for('timeslots.list_slots'))
    db.session.delete(s); db.session.commit()
    flash('Slot deleted.','info')
    return redirect(url_for('timeslots.list_slots'))
