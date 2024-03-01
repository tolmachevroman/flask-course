from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
from datetime import datetime
from database import connect_db, get_db

app = Flask(__name__)


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['POST'])
def index_post():
    date = request.form['date']  # assume date is in format 'YYYY-MM-DD'
    dt = datetime.strptime(date, '%Y-%m-%d')
    database_date = dt.strftime('%Y%m%d')

    db = get_db()
    db.execute('insert into log_date (entry_date) values (?)',
               [database_date])
    db.commit()
    return redirect(url_for('index_get'))


@app.route('/', methods=['GET'])
def index_get():
    db = get_db()
    cur = db.execute(
        'select log_date.entry_date, sum(food.protein) as protein, sum(food.carbs) as carbs, sum(food.fat) as fat, sum(food.calories) as calories from log_date \
        left join food_date on food_date.log_date_id = log_date.id left join food on food.id = food_date.food_id group by log_date.id order by log_date.entry_date desc')
    results = cur.fetchall()

    date_results = []
    for i in results:
        single_date = {}

        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')
        single_date['pretty_date'] = d.strftime('%B %d, %Y')
        single_date['entry_date'] = i['entry_date']
        single_date['protein'] = i['protein']
        single_date['carbs'] = i['carbs']
        single_date['fat'] = i['fat']
        single_date['calories'] = i['calories']
        date_results.append(single_date)

    return render_template('home.html', results=date_results)


@app.route('/view/<date>', methods=['GET'])
def view_get(date):
    db = get_db()
    cur = db.execute('select id, entry_date from log_date where entry_date = ?',
                     [date])
    result = cur.fetchone()

    entry_date = result['entry_date']
    d = datetime.strptime(str(entry_date), '%Y%m%d')
    pretty_date = d.strftime('%B %d, %Y')

    food_cur = db.execute('select id, name from food')
    food_results = food_cur.fetchall()

    log_cur = db.execute('select food.name, food.protein, food.carbs, food.fat, food.calories from log_date \
                         join food_date on food_date.log_date_id = log_date.id join food on food.id = food_date.food_id \
                         where log_date.entry_date = ?', [date])
    log_results = log_cur.fetchall()

    totals = {}
    totals['protein'] = 0
    totals['carbs'] = 0
    totals['fat'] = 0
    totals['calories'] = 0

    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbs'] += food['carbs']
        totals['fat'] += food['fat']
        totals['calories'] += food['calories']

    return render_template('day.html', entry_date=entry_date, pretty_date=pretty_date, food_results=food_results, log_results=log_results, totals=totals)


@app.route('/view/<date>', methods=['POST'])
def view_post(date):
    db = get_db()

    food_id = request.form['food-select']
    cur = db.execute(
        'select id, entry_date from log_date where entry_date = ?', [date])
    result = cur.fetchone()

    db.execute('insert into food_date (food_id, log_date_id) values (?, ?)',
               [food_id, result['id']])
    db.commit()

    return redirect(url_for('view_get', date=date))


@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()

    if request.method == 'POST':
        name = request.form['food-name']
        protein = request.form['protein']
        carbs = request.form['carbohydrates']
        fat = request.form['fat']
        calories = int(protein) * 4 + int(carbs) * 4 + int(fat) * 9

        if not name or not protein or not carbs or not fat:
            return render_template('add_food.html', message='Please enter required fields')

        db.execute('insert into food (name, protein, carbs, fat, calories) values (?, ?, ?, ?, ?)',
                   [name, protein, carbs, fat, calories])
        db.commit()

    cur = db.execute('select name, protein, carbs, fat, calories from food')
    results = cur.fetchall()

    return render_template('add_food.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
