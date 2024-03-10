from flask import Flask, g, request, jsonify
from database import get_db
from functools import wraps

app = Flask(__name__)

api_username = 'admin'
api_password = 'password'


def protected(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        else:
            return jsonify({'error': 'Authentication failed'}), 403
    return decorated_function


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.get('/members')
@protected
def get_members():
    db = get_db()
    members = db.execute(
        'select id, name, email, level from members').fetchall()
    return jsonify([{'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']} for member in members])


@app.get('/members/<int:member_id>')
def get_member(member_id):
    db = get_db()
    member = db.execute(
        'select id, name, email, level from members where id = ?', [member_id]).fetchone()
    if member:
        return jsonify({'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']})
    else:
        return jsonify({'error': 'Member not found'}), 404


@app.post('/members')
def add_member():
    new_member_data = request.json
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()
    db.execute('insert into members (name, email, level) values (?, ?, ?)', [
               name, email, level])
    db.commit()

    member = db.execute(
        'select id, name, email, level from members where name = ?', [name]).fetchone()

    return jsonify({'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']})


@app.put('/members/<int:member_id>')
def update_member(member_id):
    db = get_db()
    member = db.execute(
        'select id, name, email, level from members where id = ?', [member_id]).fetchone()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    else:
        updated_member_data = request.json
        name = updated_member_data['name']
        email = updated_member_data['email']
        level = updated_member_data['level']

        db.execute('update members set name = ?, email = ?, level = ? where id = ?', [
                   name, email, level, member_id])
        db.commit()

        return jsonify({'id': member_id, 'name': name, 'email': email, 'level': level})


@app.delete('/members/<int:member_id>')
def delete_member(member_id):
    db = get_db()
    member = db.execute(
        'select id, name, email, level from members where id = ?', [member_id]).fetchone()
    if not member:
        return jsonify({'error': 'Member not found'}), 404
    else:
        db.execute('delete from members where id = ?', [member_id])
        db.commit()
        return jsonify({'message': 'Member deleted successfully'})


if __name__ == '__main__':
    app.run(debug=True)
