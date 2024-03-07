from flask import Flask, render_template, request, redirect, url_for, g, session
from database import get_db, connect_db
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def get_current_user():
    user_result = None
    if 'user' in session:
        user = session['user']
        db = get_db()
        user_result = db.execute(
            'select id, name, is_expert, is_admin from users where name = ?', [user]).fetchone()
    return user_result

# ------------------------------
# Index Routes
# ------------------------------


@app.route('/')
def index():
    user = get_current_user()

    return render_template('home.html', user=user)

# ------------------------------
# Registration Routes
# ------------------------------


@app.get('/register')
def register_get():
    user = get_current_user()

    return render_template('register.html', user=user)


@app.post('/register')
def register_post():
    name = request.form['name']
    password = request.form['password']
    hashed_password = generate_password_hash(
        password, method='pbkdf2:sha256', salt_length=8)

    db = get_db()
    db.execute('insert into users (name, password, is_expert, is_admin) values (?, ?, ?, ?)',
               [name, hashed_password, False, False])
    db.commit()

    session['user'] = name

    return redirect(url_for('index'))

# ------------------------------
# Login Routes
# ------------------------------


@app.get('/login')
def login_get():
    user = get_current_user()

    return render_template('login.html', user=user)


@app.post('/login')
def login_post():
    name = request.form['name']
    password = request.form['password']

    db = get_db()
    user = db.execute(
        'select id, name, password from users where name = ?', [name]).fetchone()

    if user and check_password_hash(user['password'], password):
        session['user'] = user['name']
        return redirect(url_for('index'))

    return '<h1>Error!</h1>'

# ------------------------------
# Question Routes
# ------------------------------


@app.route('/question')
def question():
    user = get_current_user()

    return render_template('question.html', user=user)

# ------------------------------
# Answer Routes
# ------------------------------


@app.route('/answer')
def answer():
    user = get_current_user()

    return render_template('answer.html', user=user)

# ------------------------------
# Ask Routes
# ------------------------------


@app.get('/ask')
def ask_get():
    user = get_current_user()

    db = get_db()
    experts = db.execute(
        'select id, name from users where is_expert = True').fetchall()

    return render_template('ask.html', user=user, experts=experts)


@app.post('/ask')
def ask_post():
    user = get_current_user()
    question = request.form['question']
    expert = request.form['expert']

    db = get_db()
    db.execute('insert into questions (question, asked_by_id, expert_id) values (?, ?, ?)',
               [question, user['id'], expert])
    db.commit()

    return redirect(url_for('index'))


@app.route('/unanswered')
def unanswered():
    user = get_current_user()

    db = get_db()
    questions = db.execute(
        'select questions.id, questions.question, users.name \
         from questions join users on users.id = questions.asked_by_id \
         where questions.answer is null and questions.expert_id = ?', [user['id']]).fetchall()

    return render_template('unanswered.html', user=user, questions=questions)


@app.route('/users')
def users():
    user = get_current_user()

    db = get_db()
    users = db.execute(
        'select id, name, is_expert, is_admin from users').fetchall()

    return render_template('users.html', user=user, users=users)

# ------------------------------
# Logout Routes
# ------------------------------


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/promote/<user_id>')
def promote(user_id):
    user = get_current_user()

    if not user:
        return redirect(url_for('index'))

    db = get_db()
    db.execute('update users set is_expert = True where id = ?', [user['id']])
    db.commit()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)