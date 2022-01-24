from flask_marshmallow import Marshmallow
from marshmallow import EXCLUDE, fields, validate

from src.models import User

ma = Marshmallow()


class RegisterUserSchema(ma.Schema):
    class Meta:
        model = User
        unknown = EXCLUDE
        ordered = True

    username = fields.String(required=True, validate=validate.Length(min=3, max=50))
    email_address = fields.String(data_key='emailAddress', required=True,
                                  validate=[validate.Length(max=120), validate.Email()])
    first_name = fields.String(data_key='firstName', required=True, validate=validate.Length(max=50))
    last_name = fields.String(data_key='lastName', required=True, validate=validate.Length(max=50))
    phone = fields.String(validate=[validate.Length(max=30)])
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=8))
    is_active = fields.String(data_key='isActive')


class ForgotPasswordSchema(ma.Schema):
    class Meta:
        unknown = EXCLUDE
        ordered = True

    email_address = fields.String(
        data_key='emailAddress',
        required=True,
        validate=[validate.Length(max=120), validate.Email()]
    )


class ResetPasswordSchema(ma.Schema):
    class Meta:
        model = User
        unknown = EXCLUDE
        ordered = True

    id = fields.String(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=8))


register_user_schema = RegisterUserSchema()
forgot_password_schema = ForgotPasswordSchema()
reset_password_schema = ResetPasswordSchema()
