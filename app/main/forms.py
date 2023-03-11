# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length
from wtforms.widgets import TextArea
from ..models import Category


class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Post')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = [(c.id, c.name) for c in Category.query.all()]


class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()], widget=TextArea())
    category = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Edit Post')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category.choices = [(c.id, c.name) for c in Category.query.all()]


class CreateCommentForm(FlaskForm):
    content = StringField('Comment', widget=TextArea(), validators=[DataRequired()])
    submit = SubmitField('Submit')

class CreateCategoryForm(FlaskForm):
    name = StringField('New Category', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    text = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

