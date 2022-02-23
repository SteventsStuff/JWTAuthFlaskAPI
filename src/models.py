from __future__ import annotations

import typing as t
import uuid
import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from werkzeug.security import generate_password_hash

import log
from .mixins import UpdateMixin
from src.exceptions import DBError

logger = log.APILogger(__name__)

db = SQLAlchemy()


class User(UpdateMixin, db.Model):
    __tablename__ = 'tbl_User'

    id = db.Column(db.String(36), primary_key=True, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email_address = db.Column(db.String(120), name='emailAddress', nullable=False, unique=True)
    password_hash = db.Column(db.String(128), name='passwordHash', )
    first_name = db.Column(db.String(50), name='firstName', nullable=False)
    last_name = db.Column(db.String(50), name='lastName', nullable=False)
    phone = db.Column(db.String(30), name='phone', unique=True)
    registration_date = db.Column(db.DateTime, name='registrationDate',
                                  default=datetime.datetime.utcnow)
    is_active = db.Column(db.SMALLINT, name='isActive')

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    @classmethod
    def get_by_email_address(cls, email_address: str) -> t.Optional[User]:
        logger.debug(f'Trying to get a user by email address: {email_address}')
        return db.session.query(cls).filter(cls.email_address == email_address).first()

    @classmethod
    def get_by_id(cls, record_id: str) -> t.Optional[User]:
        logger.debug(f'Trying to get a user by id: {record_id}')
        return db.session.query(cls).filter(cls.id == record_id).first()

    @classmethod
    def get_duplicate_id(cls, user_info: t.Dict[str, t.Any]) -> t.Optional[str]:
        """Gets duplicate report ID from the DB if such exists

        Args:
            user_info (dict): User information. It must contain "email_address" and "username" fields.

        Returns:
            str (optional): Duplicate report ID from the DB if such exists, None otherwise
        """

        email = user_info['email_address']
        username = user_info['username']
        logger.debug(f'Checking if user with username: {username} or email address: {email} already exists')
        duplicate = db.session.query(cls) \
            .filter(db.or_(cls.username == email,
                           cls.email_address == username)).first()

        return duplicate.id if duplicate else None

    @classmethod
    def create_user(cls, user_info: t.Dict[str, t.Any]) -> User:
        user = cls(**user_info, id=str(uuid.uuid4()), is_active=1)
        user.save_to_db()
        return user

    def save_to_db(self):
        logger.debug(f'Trying to save user with id: {self.id} into DB...')
        try:
            db.session.add(self)
            db.session.commit()
        except exc.IntegrityError as e:
            logger.error(f'Failed to save user with id: {self.id} into DB.\nError type: {type(e)}\nError message: {e}')
            db.session.rollback()
            raise DBError(str(e))

    def __repr__(self) -> str:
        return f'<{type(self).__name__} {self.username}, {self.email_address}>'
