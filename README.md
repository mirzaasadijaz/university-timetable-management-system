# CTMS — Class Timetable Management System

A web-based timetable scheduling application with automatic **clash detection**, built with Python (Flask), SQLAlchemy, and Bootstrap 5.

---

## Features

- **Timetable Scheduling** — Create, edit, publish, and archive class schedule entries across teachers, rooms, sections, and time slots.
- **Clash Detection** — Real-time detection of three clash types: teacher double-booking, room double-booking, and section double-booking.
- **Clash Report** — A dedicated report page showing all existing conflicts in the schedule.
- **Visual Timetable Grid** — Weekly grid view filterable by section or teacher.
- **Role-Based Access Control** — Four roles with distinct permissions: `super_admin`, `admin`, `manager`, `teacher`.
- **Department Management** — Organise teachers and courses by department.
- **Import / Export** — Bulk import teachers and rooms via CSV; export the full timetable to CSV or Excel (.xlsx).
- **Pagination & Search** — All list views support search and paginated results.
- **CSRF Protection** — All forms are protected with Flask-WTF CSRF tokens.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask 3 |
| ORM | Flask-SQLAlchemy + SQLAlchemy 2 |
| Auth | Flask-Login + Flask-Bcrypt |
| Forms | Flask-WTF + WTForms |
| Migrations | Flask-Migrate (Alembic) |
| Frontend | Bootstrap 5.3 + Bootstrap Icons |
| Database | SQLite (dev) / any SQLAlchemy-compatible DB (prod) |
| Export | openpyxl, csv |
| Import | pandas, csv |

---

## Project Structure

```
ctms/
├── config.py                   # Dev / Prod / Testing config classes
├── run.py                      # App entry point
├── seed.py                     # Creates initial Super Admin account
├── .env                        # Environment variables (not committed)
├── .gitignore
├── requirements.txt
└── app/
    ├── __init__.py             # App factory, extension init, error handlers
    ├── models/
    │   ├── __init__.py         # Imports all models (required for migrations)
    │   ├── user.py
    │   ├── department.py
    │   ├── teacher.py
    │   ├── course.py
    │   ├── room.py
    │   ├── timeslot.py
    │   ├── section.py
    │   └── schedule.py         # Main ClassTimeSchedule table
    ├── blueprints/
    │   ├── auth.py
    │   ├── dashboard.py
    │   ├── users.py
    │   ├── departments.py
    │   ├── teachers.py
    │   ├── courses.py
    │   ├── rooms.py
    │   ├── timeslots.py
    │   ├── sections.py
    │   ├── schedules.py        # Includes timetable grid view
    │   ├── clashes.py
    │   └── import_export.py
    ├── services/
    │   ├── clash_detector.py
    │   ├── export_service.py
    │   └── import_service.py
    ├── utils/
    │   ├── decorators.py       # @role_required decorator
    │   └── helpers.py
    ├── templates/
    │   ├── base.html
    │   ├── _macros.html
    │   ├── auth/
    │   ├── dashboard/
    │   ├── users/
    │   ├── departments/
    │   ├── teachers/
    │   ├── courses/
    │   ├── rooms/
    │   ├── timeslots/
    │   ├── sections/
    │   ├── schedules/
    │   ├── clashes/
    │   ├── import_export/
    │   └── errors/             # 403, 404, 500 pages
    └── static/
        └── css/style.css
```

---

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ctms
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example below into a `.env` file in the project root:

```env
SECRET_KEY=change-this-to-a-random-64-char-string
DATABASE_URL=sqlite:///ctms_dev.db
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=run.py
ITEMS_PER_PAGE=20
```

> **Important:** Change `SECRET_KEY` to a long random string before deploying to production.

### 5. Initialise the database

```bash
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

### 6. Seed the Super Admin account

```bash
python seed.py
```

Default credentials created by the seed script:

| Field | Value |
|---|---|
| Username | `superadmin` |
| Password | `Admin@1234` |
| Role | `super_admin` |

> **Change this password immediately after your first login.**

### 7. Run the development server

```bash
python run.py
```

Open your browser at `http://localhost:5000`.

---

## User Roles & Permissions

| Action | super_admin | admin | manager | teacher |
|---|:---:|:---:|:---:|:---:|
| Manage users | ✅ | ✅ | — | — |
| Add / edit teachers, courses, rooms, sections | ✅ | ✅ | — | — |
| View teachers, courses, rooms, sections | ✅ | ✅ | ✅ | — |
| Add / edit schedules | ✅ | ✅ | — | — |
| View schedule & clash report | ✅ | ✅ | ✅ | — |
| Import / export data | ✅ | ✅ | ✅ | — |
| Manage time slots | ✅ | — | — | — |
| Delete any record | ✅ | — | — | — |
| View own timetable | — | — | — | ✅ |

---

## Clash Detection

The `ClashDetector` service checks three conflict types before any schedule entry is saved:

- **Teacher clash** — the same teacher is already assigned at the same time slot.
- **Room clash** — the same room is already booked at the same time slot.
- **Section clash** — the same student section already has a class at the same time slot.

If any clash is found, the entry is rejected and an error message is displayed. The **Clashes Report** (`/clashes/report`) scans the entire schedule and lists all existing conflicts grouped by type.

---

## Import / Export

### Export

Navigate to **Manage → Import / Export** and download:
- `timetable.csv` — plain CSV of all schedule entries.
- `timetable.xlsx` — formatted Excel workbook with styled headers.

### Import Teachers (CSV)

Required columns: `full_name`, `employee_code`  
Optional columns: `designation`

### Import Rooms (CSV)

Required columns: `room_number`, `building`  
Optional columns: `capacity`, `room_type`

---

## URL Reference

| URL | Description |
|---|---|
| `/` | Dashboard |
| `/login` | Login page |
| `/schedules/timetable` | Visual weekly timetable grid |
| `/schedules/` | Schedule entry list |
| `/clashes/report` | Clash report |
| `/teachers/` | Teachers list |
| `/courses/` | Courses list |
| `/rooms/` | Rooms list |
| `/sections/` | Sections list |
| `/timeslots/` | Time slots list |
| `/departments/` | Departments list |
| `/users/` | User management |
| `/data/` | Import / Export hub |

---

## Production Notes

- Set `FLASK_ENV=production` and `FLASK_DEBUG=0` in your `.env`.
- Replace `DATABASE_URL` with your production database URI (PostgreSQL recommended).
- Run behind a WSGI server such as **Gunicorn**: `gunicorn "app:create_app('production')"`.
- Use a reverse proxy (Nginx / Apache) in front of Gunicorn.
- Set a strong, random `SECRET_KEY`.

---

## License

This project is released for educational use. Adapt freely for your institution's needs.
