

from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    email = fields.Email(required=True)
    age = fields.Integer(validate=validate.Range(min=18, max=120))

user_schema = UserSchema()
