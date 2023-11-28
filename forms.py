from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,IntegerField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditorField


##WTForm
class Create(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    age = IntegerField("age", validators=[DataRequired()])
    count = StringField("count", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

class Product(FlaskForm):
    gender = IntegerField("AGE",)
