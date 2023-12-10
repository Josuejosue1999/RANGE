from flask import redirect, url_for, render_template, flash, request
from flaskapp import app, db, bcrypt
from flaskapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, TaskForm
from flaskapp.models import User, Task, Todo
from flask_login import login_user, current_user, logout_user, login_required
from PIL import Image
import secrets
import os

# my_tasks = [
#     {
#         'title': 'Homework',
#         'progress': '10%',
#         'todo': ['ToDo1', 'ToDo2', 'ToDo3', 'ToDo4', ],
#     },
#     {
#         'title': 'Homework',
#         'progress': '10%',
#         'todo': ['ToDo1', 'ToDo2', 'ToDo3', 'ToDo4', ],
#     },
#     {
#         'title': 'Homework',
#         'progress': '10%',
#         'todo': ['ToDo1', 'ToDo2', 'ToDo3', 'ToDo4', ],
#     },
# ]


@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route("/tasks", methods=['GET', 'POST'])
@login_required
def tasks(**kwargs):
    my_tasks = Task.query.all()
    todos = Todo.query.all()
    form = TaskForm()
    if form.validate_on_submit():
        task_head = Task(title=form.title.data,
                         priority=form.priority.data, creator=current_user)
        content = Todo(todo=form.content.data,
                       date_due=form.date_due.data, task_id=task_head.id)
        db.session.add(task_head)
        db.session.add(content)
        db.session.commit()
        flash('You task has been created!', 'success')
        return redirect(url_for('tasks'))
    
    update_task = Task.query.get_or_404(task.id)
    update_todo = Todo.query.get_or_404(todo.id)
    update_form = TaskForm()
    update_form.title.data = Task
    
    return render_template('tasks.html', my_tasks=my_tasks, todo=todo, form=form)


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/images', picture_fn)

    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    return picture_fn


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='images/' +
                         current_user.image_file)
    return render_template('profile.html', image_file=image_file, form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has now been created! You can now log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login unsucessful. Please check email and password', 'danger')
    return render_template('properlogin.html', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))
