"""Shared Flask extensions (single app factory pattern)."""

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()


class BaseModel(db.Model):
    """
    Abstract base for all ORM models.

    SQLAlchemy 2 rejects legacy annotations (e.g. `id: int = db.Column(...)`)
    unless they use ``Mapped[]`` or ``__allow_unmapped__`` is enabled.
    """

    __abstract__ = True
    __allow_unmapped__ = True
