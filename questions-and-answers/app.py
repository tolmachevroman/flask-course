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

    return '<h1>User created!</h1>'

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
        return '<h1>User logged in!</h1>'

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


@app.route('/ask')
def ask():
    user = get_current_user()

    return render_template('ask.html', user=user)


@app.route('/unanswered')
def unanswered():
    user = get_current_user()

    return render_template('unanswered.html', user=user)


@app.route('/users')
def users():
    user = get_current_user()

    return render_template('users.html', user=user)

# ------------------------------
# Logout Routes
# ------------------------------


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
