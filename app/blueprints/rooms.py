from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from app import db
from app.models.room       import Room
from app.utils.decorators  import role_required

rooms_bp = Blueprint('rooms', __name__)

class RoomForm(FlaskForm):
    room_number  = StringField('Room Number', validators=[DataRequired(), Length(max=20)])
    floor     = SelectField('Floor', choices=[
        ('Ground','Ground'),('First','1st'),
        ('Second','2nd'),('Third','3rd'),
        ('Fourth','4th'),('Fifth','5th')])
    building     = StringField('Building',    validators=[Length(max=80)])
    capacity     = IntegerField('Capacity',   validators=[NumberRange(1,2000)], default=40)
    room_type    = SelectField('Type', choices=[
        ('classroom','Classroom'),('lab','Lab'),
        ('seminar','Seminar Room'),('auditorium','Auditorium')])
    is_available = BooleanField('Available', default=True)
    submit       = SubmitField('Save')

@rooms_bp.route('/')
@login_required
@role_required('super_admin','admin','manager')
def list_rooms():
    search = request.args.get('search','')
    page   = request.args.get('page',1,type=int)
    q = Room.query
    if search: q = q.filter(Room.room_number.ilike(f'%{search}%')|Room.floor.ilike(f'%{search}%')|Room.building.ilike(f'%{search}%'))
    rooms = q.order_by(Room.building,Room.floor,Room.room_number).paginate(page=page,per_page=20)
    return render_template('rooms/list.html',rooms=rooms,search=search)

@rooms_bp.route('/add', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def add_room():
    form = RoomForm()
    if form.validate_on_submit():
        r = Room(room_number=form.room_number.data,floor=form.floor.data, building=form.building.data,
                 capacity=form.capacity.data, room_type=form.room_type.data,
                 is_available=form.is_available.data)
        db.session.add(r); db.session.commit()
        flash(f'Room {r.room_number} added.','success')
        return redirect(url_for('rooms.list_rooms'))
    return render_template('rooms/form.html',form=form,title='Add Room')

@rooms_bp.route('/<int:id>/edit', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def edit_room(id):
    r = Room.query.get_or_404(id)
    form = RoomForm(obj=r)
    if form.validate_on_submit():
        r.room_number=form.room_number.data; r.building=form.building.data
        r.floor=form.floor.data
        r.capacity=form.capacity.data; r.room_type=form.room_type.data
        r.is_available=form.is_available.data
        db.session.commit(); flash('Room updated.','success')
        return redirect(url_for('rooms.list_rooms'))
    return render_template('rooms/form.html',form=form,title='Edit Room')

@rooms_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@role_required('super_admin')
def delete_room(id):
    r = Room.query.get_or_404(id)
    if r.schedule_entries:
        flash('Cannot delete: room has schedule entries.','danger')
        return redirect(url_for('rooms.list_rooms'))
    db.session.delete(r); db.session.commit()
    flash('Room deleted.','info')
    return redirect(url_for('rooms.list_rooms'))
