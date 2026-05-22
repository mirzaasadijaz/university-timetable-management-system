from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login      import LoginManager
from flask_wtf        import CSRFProtect
from flask_migrate    import Migrate
from flask_bcrypt     import Bcrypt
from config           import config

db      = SQLAlchemy()
login   = LoginManager()
csrf    = CSRFProtect()
migrate = Migrate()
bcrypt  = Bcrypt()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialise extensions
    db.init_app(app)
    login.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    login.login_view             = 'auth.login'
    login.login_message          = 'Please log in to access this page.'
    login.login_message_category = 'warning'

    # ── Import all models (must happen inside app context) ──
    with app.app_context():
        from app import models  # noqa — registers all tables with SQLAlchemy

    # ── Register blueprints ──
    from app.blueprints.auth          import auth_bp
    from app.blueprints.dashboard     import dashboard_bp
    from app.blueprints.users         import users_bp
    from app.blueprints.teachers      import teachers_bp
    from app.blueprints.courses       import courses_bp
    from app.blueprints.rooms         import rooms_bp
    from app.blueprints.timeslots     import timeslots_bp
    from app.blueprints.sections      import sections_bp
    from app.blueprints.schedules     import schedules_bp
    from app.blueprints.clashes       import clashes_bp
    from app.blueprints.import_export import ie_bp
    from app.blueprints.departments   import departments_bp
    from app.blueprints.main          import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp,        url_prefix='/users')
    app.register_blueprint(teachers_bp,     url_prefix='/teachers')
    app.register_blueprint(courses_bp,      url_prefix='/courses')
    app.register_blueprint(rooms_bp,        url_prefix='/rooms')
    app.register_blueprint(timeslots_bp,    url_prefix='/timeslots')
    app.register_blueprint(sections_bp,     url_prefix='/sections')
    app.register_blueprint(schedules_bp,    url_prefix='/schedules')
    app.register_blueprint(clashes_bp,      url_prefix='/clashes')
    app.register_blueprint(ie_bp,           url_prefix='/data')
    app.register_blueprint(departments_bp,  url_prefix='/departments')

    # ── Jinja2 context processor — inject current year and role helper ──
    from datetime import datetime
    @app.context_processor
    def inject_globals():
        return {'current_year': datetime.utcnow().year}

    # ── Error handlers ──
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500

    return app
