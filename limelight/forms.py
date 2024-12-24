from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class NewProjectForm(FlaskForm):
    slug: str = StringField("slug", validators=[DataRequired()])
    origen: str = StringField("origen", validators=[DataRequired()])
