# Import all models here so SQLAlchemy registers them.
# This file is imported by app/__init__.py via the blueprint imports.

from app.models.user       import User        # noqa: F401
from app.models.department import Department  # noqa: F401
from app.models.teacher    import Teacher, teacher_courses  # noqa: F401
from app.models.course     import Course, section_courses   # noqa: F401
from app.models.room       import Room        # noqa: F401
from app.models.timeslot   import TimeSlot    # noqa: F401
from app.models.section    import Section     # noqa: F401
from app.models.schedule   import ClassTimeSchedule  # noqa: F401
