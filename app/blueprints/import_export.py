from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.services.export_service import export_csv, export_excel
from app.services.import_service import import_teachers, import_rooms
from app.utils.decorators import role_required

ie_bp = Blueprint('import_export', __name__)

@ie_bp.route('/')
@login_required
@role_required('super_admin','admin','manager')
def index():
    return render_template('import_export/index.html')

@ie_bp.route('/export/csv')
@login_required
@role_required('super_admin','admin','manager')
def export_schedule_csv():  return export_csv()

@ie_bp.route('/export/excel')
@login_required
@role_required('super_admin','admin','manager')
def export_schedule_excel(): return export_excel()

@ie_bp.route('/import/teachers', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def import_teachers_view():
    results = None; imported = 0
    if request.method == 'POST':
        f = request.files.get('csv_file')
        if not f or not f.filename.endswith('.csv'):
            flash('Please upload a .csv file.','danger')
            return redirect(request.url)
        results, imported = import_teachers(f)
        flash(f'Done: {imported} teachers imported.','success')
    return render_template('import_export/import_teachers.html',
        results=results, imported=imported)

@ie_bp.route('/import/rooms', methods=['GET','POST'])
@login_required
@role_required('super_admin','admin')
def import_rooms_view():
    results = None; imported = 0
    if request.method == 'POST':
        f = request.files.get('csv_file')
        if not f or not f.filename.endswith('.csv'):
            flash('Please upload a .csv file.','danger')
            return redirect(request.url)
        results, imported = import_rooms(f)
        flash(f'Done: {imported} rooms imported.','success')
    return render_template('import_export/import_rooms.html',
        results=results, imported=imported)
