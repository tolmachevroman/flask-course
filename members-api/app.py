from flask import Flask, g, request, jsonify
from database import get_db

app = Flask(__name__)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.get('/members')
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
    return f'member {member_id} updated'


@app.delete('/members/<int:member_id>')
def delete_member(member_id):
    return f'member {member_id} deleted'


if __name__ == '__main__':
    app.run(debug=True)
