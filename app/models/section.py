"""Student sections / cohorts — linked to schedules; section + timeslot clash detection."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from app.extensions import BaseModel, db

if TYPE_CHECKING:
    from app.models.schedule import Schedule


class Section(BaseModel):
    """
    Class section or student group (e.g. CS-3A).

    Relationships:
        - schedules: one-to-many (class_time_schedule)
    """

    __tablename__ = "sections"

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(50), unique=True, nullable=False, index=True)
    program: Optional[str] = db.Column(db.String(120), nullable=True)
    semester: Optional[str] = db.Column(db.String(20), nullable=True)
    academic_year: Optional[str] = db.Column(db.String(20), nullable=True)
    strength: int = db.Column(db.Integer, nullable=False, default=0)
    is_active: bool = db.Column(db.Boolean, nullable=False, default=True)
    created_at: datetime = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    schedules: List[Schedule] = db.relationship(
        "Schedule",
        back_populates="section",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Section id={self.id} name={self.name!r}>"

    # -------------------------------------------------------------------------
    # Display helpers
    # -------------------------------------------------------------------------

    @property
    def label(self) -> str:
        """Display label including program context when available."""
        if self.program:
            return f"{self.name} ({self.program})"
        return self.name

    # -------------------------------------------------------------------------
    # Schedule / clash-detection helpers
    # -------------------------------------------------------------------------

    def schedules_at_timeslot(self, time_slot_id: int):
        """All class_time_schedule rows for this section in a given slot."""
        return [s for s in self.schedules if s.time_slot_id == time_slot_id]

    def is_busy_at_timeslot(
        self, time_slot_id: int, exclude_schedule_id: Optional[int] = None
    ) -> bool:
        """
        True if section already has a schedule in time_slot_id.
        Used for section_id + time_slot_id clash detection.
        """
        for schedule in self.schedules_at_timeslot(time_slot_id):
            if exclude_schedule_id is None or schedule.id != exclude_schedule_id:
                return True
        return False
from app import db
from app.models.course import section_courses

class Section(db.Model):
    __tablename__ = 'sections'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(50), nullable=False)
    program  = db.Column(db.String(80), nullable=False)
    semester = db.Column(db.Integer, nullable=False, default=1)
    strength = db.Column(db.Integer, nullable=False, default=0)

    courses  = db.relationship('Course', secondary=section_courses,
                  backref=db.backref('sections', lazy='dynamic'))
    schedules= db.relationship('ClassTimeSchedule', backref='section', lazy='dynamic')

    def __repr__(self): return f'<Section {self.name}>'
