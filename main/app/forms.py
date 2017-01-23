from flask_wtf import Form
from wtforms import StringField, BooleanField,SubmitField
from wtforms.validators import DataRequired

class LoginForm(Form):
    api_name = StringField('API NAME', validators=[DataRequired()])
    method = StringField('METHOD', validators=[DataRequired()])
    endpoint = StringField('ENDPOINT',validators=[DataRequired()])
    maintainer = StringField('MAINTAINER',validators=[DataRequired()])
    payload = StringField('PAYLOAD')
    output = StringField('OUTPUT')

class EditForm(Form):
    #api_id = StringField('api_id',validators=[DataRequired()])
    api_name = StringField('API NAME')
    method = StringField('METHOD')
    endpoint = StringField('END-POINT')
    maintainer = StringField('MAINTAINER')
    payload = StringField('PAYLOAD')
    output = StringField('OUTPUT')
    checkbox = BooleanField('DELETE')

class TableForm(Form):
    starting = SubmitField(label='Starting')
    
class EditForm1(Form):
    #api_id = StringField('api_id',validators=[DataRequired()])
    api_name = StringField('api_name')
    method = StringField('method')
    endpoint = StringField('endpoint')
    maintainer = StringField('maintainer')
    payload = StringField('payload')
    output = StringField('output')
    checkbox = BooleanField('delete')
class ContactForm(Form):
	name = StringField('Name', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired()])
	message = StringField('Message', validators=[DataRequired()])
