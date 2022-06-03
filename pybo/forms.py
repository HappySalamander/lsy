from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, EmailField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class QuestionForm(FlaskForm):
    subject = StringField('제목', validators=[DataRequired('제목은 필수입력 항목입니다.')])
    category = SelectField('카테고리', choices=[('CU', 'CU'), ('GS25', 'GS25'), ('미니스탑', '미니스탑'), ('세븐일레븐', '세븐일레븐') ])
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수입력 항목입니다.')])

class AnswerForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('내용은 필수입력 항목입니다.')])

class UserCreateForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=3, max=25)])
    password1 = PasswordField('비밀번호', validators=[
        DataRequired(), EqualTo('password2', '비밀번호가 일치하지 않습니다')])
    password2 = PasswordField('비밀번호확인', validators=[DataRequired()])
    email = EmailField('이메일', validators=[DataRequired(), Email()])

class UserLoginForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('비밀번호', validators=[DataRequired()])