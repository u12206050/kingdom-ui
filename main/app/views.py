from flask import render_template, flash, redirect, request
from .forms import LoginForm,EditForm,TableForm,EditForm1,ContactForm
from app import app
import redis_db
from slacker import Slacker
import ConfigParser
import pygal
from pygal.style import BlueStyle


@app.route('/')
@app.route('/index')
def index():
    keys,values = redis_db.get_keys_value()
    values = map(int,values)
    bar_chart = pygal.Bar(width=800, height=400,explicit_size=True, title='Efficiency',style=BlueStyle,disable_xml_declaration=True)
    bar_chart.x_labels = keys
    bar_chart.add("Api ID's", values)
    
    cursor = redis_db.get_value()
    return render_template('index.html',title='Kingdom',cursor=cursor,bar_chart=bar_chart)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Name="%s", Method="%s",Endpoint="%s",maintainer="%s"' %
              (form.api_name.data, form.method.data,form.endpoint.data,form.maintainer.data))
        redis_db.insert_value(form.api_name.data, form.method.data,form.endpoint.data,form.maintainer.data,form.payload.data,form.output.data)
        return redirect('/index')
    return render_template('login.html',
                           title='Api Config',
                           form=form)

'''
@app.route('/charts', methods=['GET','POST'])
def charts():
    keys,values = redis_db.get_keys_value()
    values = map(int,values)
    bar_chart = pygal.Bar(width=800, height=400,explicit_size=True, title='Efficiency',style=BlueStyle,disable_xml_declaration=True)
    bar_chart.x_labels = keys
    bar_chart.add("Api ID's", values)
    return render_template('chart.html',title='Chart',bar_chart=bar_chart)



@app.route('/details', methods=['GET','POST'])
def details():
    cursor = redis_db.get_value()
    return render_template('details.html',title='Details_api',cursor=cursor,user = 'Ekansh')
'''
@app.route('/contact', methods=['GET','POST'])
def contact():
    config = ConfigParser.ConfigParser()
    config.read('slacker_data.ini')
    slacker_token = config.get('Slacker','token')
    slack = Slacker(slacker_token)
    form = ContactForm()
    if form.validate_on_submit():
        message = 'Feedback: \nName: '+str(form.name.data) + '\nEmail: ' + str(form.email.data)+ '\nMessage: ' + str(form.message.data)
        slack.chat.post_message(channel='@ekansh.singh', text=message, username='Kingdom',icon_url='https://s28.postimg.org/6sxgjs4jh/king.png')
        return redirect('/index')
    return render_template('contact.html',
                           title='Contact',
                           form=form)



@app.route('/edits/<user_id>/', methods=['GET', 'POST'])
def edits(user_id):
    form = EditForm()
    data = redis_db.get_data(user_id)
    form.api_name.data = data['name']
    form.method.data = data['method']
    form.endpoint.data = data['endpoint']
    form.maintainer.data = data['maintainer']
    form.payload.data = data['payload']
    form.output.data = data['output']
    if form.validate_on_submit():
        redis_db.update_value(user_id,form.api_name.data, form.method.data,form.endpoint.data,form.maintainer.data,form.payload.data,form.output.data,form.checkbox.data)
        return redirect('/index')
    return render_template('edit.html',
                           title='EDIT APIs',
                           form=form,api_id = user_id)



