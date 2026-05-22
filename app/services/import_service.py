import csv, io
from app import db
from app.models.teacher  import Teacher
from app.models.course   import Course
from app.models.room     import Room
from app.models.section  import Section

def _read(file):
    return csv.DictReader(io.StringIO(file.stream.read().decode('utf-8')))

def import_teachers(file):
    results = []; imported = 0
    for i, row in enumerate(_read(file), 2):
        try:
            if not row.get('full_name') or not row.get('employee_code'):
                results.append({'row':i,'status':'error','msg':'Missing full_name/employee_code'}); continue
            if Teacher.query.filter_by(employee_code=row['employee_code'].strip()).first():
                results.append({'row':i,'status':'skipped','msg':f'Code {row["employee_code"]} exists'}); continue
            t = Teacher(full_name=row['full_name'].strip(),
                        employee_code=row['employee_code'].strip(),
                        designation=row.get('designation','Lecturer').strip())
            db.session.add(t); imported += 1
            results.append({'row':i,'status':'ok','msg':t.full_name})
        except Exception as e:
            results.append({'row':i,'status':'error','msg':str(e)})
    db.session.commit()
    return results, imported

def import_rooms(file):
    results = []; imported = 0
    for i, row in enumerate(_read(file), 2):
        try:
            if not row.get('room_number') or not row.get('building'):
                results.append({'row':i,'status':'error','msg':'Missing room_number/building'}); continue
            r = Room(room_number=row['room_number'].strip(),
                     building=row['building'].strip(),
                     capacity=int(row.get('capacity',40)),
                     room_type=row.get('room_type','classroom').strip())
            db.session.add(r); imported += 1
            results.append({'row':i,'status':'ok','msg':r.room_number})
        except Exception as e:
            results.append({'row':i,'status':'error','msg':str(e)})
    db.session.commit()
    return results, imported
