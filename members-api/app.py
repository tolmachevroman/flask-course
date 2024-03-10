from flask import Flask

app = Flask(__name__)


@app.get('/members')
def get_members():
    return 'members list'


@app.get('/members/<int:member_id>')
def get_member(member_id):
    return f'member {member_id}'


@app.post('/members')
def add_member():
    return 'member created'


@app.put('/members/<int:member_id>')
def update_member(member_id):
    return f'member {member_id} updated'


@app.delete('/members/<int:member_id>')
def delete_member(member_id):
    return f'member {member_id} deleted'


if __name__ == '__main__':
    app.run(debug=True)
