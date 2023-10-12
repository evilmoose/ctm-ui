from flask import Flask, render_template, redirect, session, jsonify,  url_for, flash, json

from todoist_api_python.api import TodoistAPI

from dotenv import load_dotenv
import os

from models import connect_db, db, User

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
    
    dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '/Users/ronni/Application/tarea-ui/files')
    
    file_names = [f for f in os.listdir(dir_path) if f.endswith('.txt')]
    
    tasks = []
    for file_name in file_names:
        with open(os.path.join(dir_path, file_name), 'r') as file:
            content = file.read()
            tasks.append({'id': file_name, 'data': content})

    return render_template('tasks.html', tasks=tasks)

def getTasks():
    api = TodoistAPI(TODOIST_TOKEN)

    try:
        tasks = api.get_tasks()
        tasks_json = [task.to_dict() for task in tasks]
        print(tasks_json)

        tasksToFiles(tasks_json)

    except Exception as error:
        print(error)

@app.route('/converted', methods=['GET'])
def converted():

    dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '/Users/ronni/Application/tarea-ui/files')
    
    file_names = [f for f in os.listdir(dir_path) if f.endswith('.json')]
    
    tasks = []
    for file_name in file_names:
        with open(os.path.join(dir_path, file_name), 'r') as file:
            content = file.read()
            tasks.append({'id': file_name, 'data': content})

    return render_template('converted.html', tasks=tasks)

@app.route('/convert/<task_id>', methods=['POST'])
def convert(task_id):

    dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '/Users/ronni/Application/tarea-ui/files')
    file_path = os.path.join(dir_path, task_id)
    
    with open(file_path, 'r') as file:
        content = file.readlines()
    
    task_data = {}
    for i in range(0, len(content) - 1, 2):
        key = content[i].strip().replace('*', '')
        value = content[i + 1].strip() if i + 1 < len(content) else ""
        task_data[key] = value

    json_file_path = os.path.join(dir_path, f"{task_id.replace('.txt', '.json')}")
    with open(json_file_path, 'w') as json_file:
        json.dump(task_data, json_file)

    flash("Task successfully converted!", 'success')
    return redirect(url_for('tasks'))

def tasksToFiles(tasks):
    for i, task in enumerate(tasks):

        content = task.get('content', '')

        filename = f'./files/task_{i+1}.txt'
        
        with open(filename, 'w') as f:
            f.write(content)

if __name__ == '__main__':
    app.run(debug=True)