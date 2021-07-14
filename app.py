import os
from flask import (
    Flask, flash, render_template, 
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists('env.py'):
    import env


app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')
app.secret_key = os.environ.get('SECRET_KEY')

mongo = PyMongo(app)


@app.route('/')
@app.route('/home')
def home():
    

@app.route('/get_lessons')
def get_lessons():
    
    hours = mongo.db.lessons.find({}, {'_id': 0, 'hours': 1})
    sum = 0
    for hour in hours:
        hour_num = float(hour['hours'])
        sum = sum + hour_num

    lessons = mongo.db.lessons.find()
    return render_template('lessons.html', lessons=lessons, sum=sum)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()})

        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))

        register = {
            'username': request.form.get('username').lower(),
            'password': generate_password_hash(request.form.get('password')),
            'first_name': request.form.get('first_name'),
            'last_name': request.form.get('last_name'),
            'email_address': request.form.get('email_address'),
            'address_line_1': request.form.get('address_line_1'),
            'address_line_2': request.form.get('address_line_2'),
            'address_city': request.form.get('address_city'),
            'address_post_code': request.form.get('address_post_code')
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session['user'] = request.form.get('username').lower()
        flash('Registration Successful!')
        return redirect(url_for('profile', username=session['user']))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()})
        
        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user['password'], request.form.get('password')):
                    session['user'] = request.form.get('username').lower()
                    flash('Welcome, {}'.format(
                        request.form.get('username')))
                    return redirect(url_for(
                        'profile', username=session['user']))

            else:
                # invalid password match
                flash('Incorrect Username and/or Password')
                return redirect(url_for('login'))
            
        else:
            # username doesn't exist
            flash('Incorrect Username and/or Password')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    # grab the sessions user's username from the db
    username = mongo.db.users.find_one(
        {'username': session['user']})['username']

    if session['user']:
        return render_template('profile.html', username=username)

    return render_template(url_for('login'))


@app.route('/logout')
def logout():
    # remove user from session cookies
    flash('You have been logged out')
    session.pop('user')
    return redirect(url_for('login'))


@app.route('/new_record', methods=['GET', 'POST'])
def new_record():
    if request.method == 'POST':
        hours = request.form.get('hours')
        mileage = 'Yes' if request.form.get('mileage') else 'No'
        expenses = 'Yes' if request.form.get('expenses') else 'No'
        
        if float(hours) < 1.5:
            lesson_expense = 7.2
        else:
            lesson_expense = str(round(float(hours) * 4.8, 2))

        record = {
            'lesson_date': request.form.get('lesson_date'),
            'lesson_start': request.form.get('lesson_start'),
            'lesson_finish': request.form.get('lesson_finish'),
            'hours': hours,
            'lesson_type': request.form.get('lesson_type'),
            'mileage': mileage,
            'expenses': expenses,
            'entry_by': session['user'],
            'lesson_expense': lesson_expense
        }

        mongo.db.lessons.insert_one(record)
        flash('Record successfully Added')
        return redirect(url_for('get_lessons'))

    categories = mongo.db.lesson_type.find().sort('lesson_type', 1)
    return render_template('new_record.html', categories=categories)


@app.route('/edit_record/<lesson_id>', methods=['GET', 'POST'])
def edit_record(lesson_id):
    if request.method == 'POST':
        hours = request.form.get('hours')
        mileage = 'Yes' if request.form.get('mileage') else 'No'
        expenses = 'Yes' if request.form.get('expenses') else 'No'
        
        if float(hours) < 1.5:
            lesson_expense = 7.2
        else:
            lesson_expense = str(round(float(hours) * 4.8, 2))

        record = {
            'lesson_date': request.form.get('lesson_date'),
            'lesson_start': request.form.get('lesson_start'),
            'lesson_finish': request.form.get('lesson_finish'),
            'hours': hours,
            'lesson_type': request.form.get('lesson_type'),
            'mileage': mileage,
            'expenses': expenses,
            'entry_by': session['user'],
            'lesson_expense': lesson_expense
        }

        mongo.db.lessons.update({'_id': ObjectId(lesson_id)}, record)
        flash('Record successfully Updated')

    lesson = mongo.db.lessons.find_one({'_id': ObjectId(lesson_id)})
    categories = mongo.db.lesson_type.find().sort('lesson_type', 1)
    return render_template('edit_record.html', lesson=lesson, categories=categories)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
