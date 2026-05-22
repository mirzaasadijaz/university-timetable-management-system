from flask import Blueprint, render_template
from flask_login import login_required
from app.services.clash_detector import ClashDetector
from app.utils.decorators import role_required

clashes_bp = Blueprint('clashes', __name__)

@clashes_bp.route('/report')
@login_required
@role_required('super_admin','admin','manager')
def report():
    clashes = ClashDetector.get_all_clashes()
    total   = sum(len(v) for v in clashes.values())
    return render_template('clashes/report.html', clashes=clashes, total=total)
