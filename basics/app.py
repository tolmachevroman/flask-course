from flask import Flask, jsonify, request, url_for, redirect, session, render_template, g
import sqlite3

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = "Thisisasecret!"


def connect_db():
    sql = sqlite3.connect(
        '/Users/romantolmachev/Github/flask-course/basics/data.db')
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, 'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        g.pop('sqlite_db')


@app.route('/')
def index():
    return '<h1>Hello, World!</h1>'


@app.route('/home', methods=['GET', 'POST'], defaults={'name': 'Default'})
@app.route('/home/<string:name>', methods=['GET', 'POST'])
def home(name):
    session['name'] = name
    db = get_db()
    cur = db.execute('select id, name, location from users')
    results = cur.fetchall()
    return render_template('home.html', name=name, display=False, mylist=[1, 2, 3, 4, 5], results=results)


@app.route('/json')
def json():
    if 'name' in session:
        name = session['name']
    else:
        name = 'Name not in session'
    return jsonify({'key': 'value', 'key2': [1, 2, 3], 'name': name})


@app.route('/query')
def query():
    name = request.args.get('name')
    location = request.args.get('location')
    return '<h1>Hi {}. You are from {}. You are on the query page</h1>'.format(name, location)


@app.route('/theform', methods=['GET', 'POST'])
def theform():
    if request.method == 'GET':
        return render_template('form.html')
    else:
        name = request.form['name']
        location = request.form['location']

        db = get_db()
        db.execute('insert into users (name, location) values (?, ?)', [
                   name, location])
        db.commit()

        return '<h1>Hello {}. You are from {}. You have submitted the form successfully</h1>'.format(name, location)


@app.route('/processjson', methods=['POST'])
def processjson():
    data = request.get_json()
    name = data['name']
    location = data['location']
    randomlist = data['randomlist']
    return jsonify({'result': 'Success', 'name': name, 'location': location, 'randomkeyinlist': randomlist[1]})


@app.route('/viewresults')
def viewresults():
    db = get_db()
    cur = db.execute('select id, name, location from users')
    results = cur.fetchall()

    return '<h1>The ID is {}. The name is {}. The location is {}</h1>'.format(results[0]['id'], results[0]['name'], results[0]['location'])


if __name__ == '__main__':
    app.run()
