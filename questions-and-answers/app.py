from flask import Flask, render_template, request, redirect, url_for, g
from database import get_db, connect_db
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    return render_template('home.html')

# ------------------------------
# Registration Routes
# ------------------------------


@app.get('/register')
def register_get():
    return render_template('register.html')


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
    return render_template('login.html')


@app.post('/login')
def login_post():
    name = request.form['name']
    password = request.form['password']

    db = get_db()
    user = db.execute(
        'select id, name, password from users where name = ?', [name]).fetchone()

    if user and check_password_hash(user['password'], password):
        return '<h1>User logged in!</h1>'

    return '<h1>Error!</h1>'

# ------------------------------
# Question Routes
# ------------------------------


@app.route('/question')
def question():
    return render_template('question.html')

# ------------------------------
# Answer Routes
# ------------------------------


@app.route('/answer')
def answer():
    return render_template('answer.html')


@app.route('/ask')
def ask():
    return render_template('ask.html')


@app.route('/unanswered')
def unanswered():
    return render_template('unanswered.html')


@app.route('/users')
def users():
    return render_template('users.html')


if __name__ == '__main__':
    app.run(debug=True)
