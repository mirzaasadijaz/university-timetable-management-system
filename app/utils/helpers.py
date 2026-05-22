from flask import current_app
from app.models.user import ROLES

def get_creatable_roles(current_role):
    """Return list of roles a given role is allowed to create."""
    hierarchy = {
        'super_admin': ['super_admin', 'admin', 'manager', 'teacher'],
        'admin':       ['manager', 'teacher'],
        'manager':     [],
        'teacher':     [],
    }
    return hierarchy.get(current_role, [])

def paginate_query(query, page, per_page=None):
    """Helper wrapper around SQLAlchemy paginate."""
    per_page = per_page or current_app.config['ITEMS_PER_PAGE']
    return query.paginate(page=page, per_page=per_page, error_out=False)
