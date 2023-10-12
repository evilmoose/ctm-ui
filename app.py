from flask import Flask, render_template, redirect, session, jsonify,  url_for, flash, json

from todoist_api_python.api import TodoistAPI

from dotenv import load_dotenv
import os

from models import connect_db, db, User, Task

from forms import SignupForm, LoginForm

load_dotenv()

app = Flask(__name__)

TODOIST_TOKEN = os.getenv("API_TOKEN")

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ronaldlopez:123456@localhost:5432/tarea"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "shhhhh"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

with app.app_context():
    db.create_all()

@app.route('/')
def dashboard():
    if "username" not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

#################################################################
####################### Login Routes ############################
#################################################################

@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User.signup(form.username.data, form.email.data, form.password.data)
        db.session.commit()
        session["username"] = user.username
        return redirect(url_for('dashboard'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            session["username"] = user.username
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.", 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for('login'))

#################################################################
####################### API Routes ##############################
#################################################################

@app.route('/tasks', methods=['GET'])
def tasks():
    getTasks()

    return render_template('tasks.html')

def getTasks():
    api = TodoistAPI(TODOIST_TOKEN)

    try:
        tasks = api.get_tasks()
        tasks_json = [task.to_dict() for task in tasks]
        print(tasks_json)

    except Exception as error:
        print(error)

@app.route('/converted', methods=['GET'])
def converted():

    return render_template('converted.html')

@app.route('/convert/<task_id>', methods=['POST'])
def convert(task_id):

    return redirect(url_for('tasks'))

if __name__ == '__main__':
    app.run(debug=True)