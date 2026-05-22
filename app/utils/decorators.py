from functools import wraps
from flask import abort, flash
from flask_login import current_user

def role_required(*roles):
    """Restrict a route to one or more roles.
    Usage:  @role_required('super_admin', 'admin')
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                flash('Access denied: insufficient permissions.', 'danger')
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator
