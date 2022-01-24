from __future__ import annotations

import uuid
import datetime
import typing as t

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from werkzeug.security import generate_password_hash

from .mixins import UpdateMixin
from src.exceptions import DBError

db = SQLAlchemy()


class User(UpdateMixin, db.Model):
    __tablename__ = 'tbl_User'

    id = db.Column(db.String(36), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email_address = db.Column(db.String(120), name='emailAddress', nullable=False, unique=True)
    password_hash = db.Column(db.String(128), name='passwordHash', )
    first_name = db.Column(db.String(50), name='firstName', nullable=False)
    last_name = db.Column(db.String(50), name='lastName', nullable=False)
    phone = db.Column(db.String(30), name='phone', unique=True)
    first_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_active = db.Column(db.SMALLINT, name='isActive')

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    @classmethod
    def get_by_email_address(cls, email_address: str) -> t.Optional[User]:
        return db.session.query(cls).filter(cls.email_address == email_address).first()

    @classmethod
    def get_by_id(cls, record_id: str) -> t.Optional[User]:
        return db.session.query(cls).filter(cls.id == record_id).first()

    @classmethod
    def is_already_exists(cls, user_info: t.Dict[str, t.Any]) -> t.Optional[int]:
        duplicate = db.session.query(cls) \
            .filter(db.or_(cls.username == user_info['username'],
                           cls.email_address == user_info['email_address'])).first()

        return duplicate.id if duplicate else None

    @classmethod
    def create(cls, user_info: t.Dict[str, t.Any]):
        user_info.update({
            'id': str(uuid.uuid4()),
        })
        # todo: Exception
        try:
            record = cls(**user_info)
        except Exception as e:
            print(type(e))
            raise DBError(str(e))

        return record

    def save_to_db(self):
        try:
            db.session.add(self)
            db.session.commit()
        except exc.IntegrityError as e:
            print(type(e))
            db.session.rollback()
            raise DBError(str(e))

    def __repr__(self) -> str:
        return f'<{type(self).__name__} {self.username}>'
