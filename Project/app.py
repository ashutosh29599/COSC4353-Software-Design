from collections import UserDict
from threading import get_ident
from flask import Flask, render_template, request, url_for, g, session, redirect, flash
import price_module

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import random, string

from flask_bcrypt import Bcrypt

# from wtforms import Form, BooleanField, StringField, PasswordField, validators


app = Flask(__name__)
app.secret_key ="123"
bcrypt = Bcrypt(app)

app.config['postgreSQL_pool'] = psycopg2.pool.SimpleConnectionPool(1, 20,
                                                                   user="postgres",
                                                                   password="postgres29",
                                                                   host="localhost",
                                                                   port=5432,
                                                                   database="fuel_app")

def get_db():
    if 'db' not in g:
        g.db = app.config['postgreSQL_pool'].getconn()
    return g.db


# Used to create an alphanumeric primary key
def genID(length):
    id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])
    return id

@app.teardown_appcontext
def close_conn(e):
    db = g.pop('db', None)
    if db is not None:
        app.config['postgreSQL_pool'].putconn(db)


@app.route('/', methods=['POST', 'GET'])
def index():
    session['signed_in'] = False
    if request.method == "POST":
        if request.form.get('login') == 'Log in':
            username = request.form.get('username')
            password = request.form.get('password')

            command = f"SELECT password FROM customer\
                        WHERE username = '{username}';" # Fetching the password hash 

            db = get_db()
            cursor = db.cursor()
            cursor.execute(command)
            table_data = cursor.fetchone()  # table_data[0] is the pwd hash
            cursor.close()
        
            if not bcrypt.check_password_hash(table_data[0], password): # incorrect username or pwd
                output_msg = "Incorrect username or password. Please try again!"
                flash(output_msg, 'error')
                return redirect(url_for("index"))
            else:   # correct username and pwd
                session['signed_in'] = True
                # return redirect(url_for("client_profile_management"))
                return redirect(url_for('logged_in'))

            # return render_template('index.html')
            # return redirect(url_for("index"))
        
        elif request.form.get('signup') == 'Sign up':
            return redirect(url_for("signup"))

        elif request.form.get('manage_profile') == 'Manage Profile':
            if not session['signed_in']:
                output_msg = "You must sign in or sign up before you can manage your profile."
                flash(output_msg, 'error')
                return redirect(url_for("index"))

            return redirect(url_for("client_profile_management"))

    else: # method == GET
        return render_template('index.html')

@app.route('/signup', methods=["POST", "GET"])
def signup():
        
    if request.method == "POST":
        if request.form.get('register') == 'Register':
            session['username'] = request.form.get('username')
            encrypted_pwd = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
            session['password'] = encrypted_pwd
            
            db = get_db()
            cursor = db.cursor()

            # Check username for duplicates
            command = f"SELECT * FROM customer \
                        WHERE username = '{session['username']}';"
            cursor.execute(command)
            table_data = len(cursor.fetchall()) # number of users with the same usernames; Max should be 1

            if table_data != 0:
                output_msg = "This username is already in use by another user.\
                    Please choose another username."
                flash(output_msg, 'error')
                return render_template("signup.html")
            # END check username

            # Create a unique id for the primary key
            session['customer_id'] = genID(16)
            command = "INSERT INTO customer VALUES "\
                      f"('{session['customer_id']}', '' , '{session['username']}', '{session['password']}')"

            cursor.execute(command)
            db.commit()
            cursor.close()

            output_msg = "You've successfully signed up! You now need to login\
                    to complete your profile info before you can request a quote."
            flash(output_msg, 'success')

            return render_template('signup.html')

        elif request.form.get('back') == 'Back':
            return redirect(url_for('index'))

        elif request.form.get('manage_profile') == 'Manage Profile':
            if not session['signed_in']:
                output_msg = "You must sign in or sign up before you can manage your profile."
                flash(output_msg, 'error')
                return redirect(url_for("signup"))

            return redirect(url_for("client_profile_management"))

    return render_template('signup.html')


@app.route('/logged_in', methods=["POST", "GET"])
def logged_in():
    output_msg = "You've successfully logged in! You will now need to \
                complete your profile if you haven't done so before you can request a quote!"
    flash(output_msg, 'error')

    if request.method == "POST":
        if request.form.get('manage_profile') == 'Manage Profile':
            return redirect(url_for("client_profile_management"))
        
        # elif request.form.get('fuel_quote_form') == 'Fuel Quote Form':
        #     return redirect(url_for("fuel_quote_form"))

        elif request.form.get('fuel_quote_history') == 'Fuel Quote History':
            return redirect(url_for("fuel_quote_history"))

    return render_template('logged_in.html')

@app.route('/client_profile_management', methods=["POST", "GET"])
def client_profile_management():
    if request.method == "POST":
        session['name'] = request.form['name']
        session['address1'] = request.form['address1']
        session['address2'] = request.form['address2']
        session['city'] = request.form['city']
        session['state'] = request.form.get('state')
        session['zipcode'] = request.form['zipcode']
    
        # Zipcode should be 5 digits long/
        zip_count = 0
        for _ in session['zipcode']:
            zip_count += 1
        if zip_count != 5:
            flash("Zipcode must be 5 digits long!")
            return render_template('client_profile_mgmt.html',\
                                    name=session['name'], address1=session['address1'],\
                                    address2=session['address2'], city=session['city'], state=session['state'])
        
        # State needs to be selected
        if session['state'] == "-":
            flash("You need to select a state!")
            return render_template('client_profile_mgmt.html',\
                                    name=session['name'], address1=session['address1'],\
                                    address2=session['address2'], city=session['city'], zipcode=session['zipcode'])


        # Send the data to the db
        session['user_id'] = genID(16)
        command = "INSERT INTO user_details VALUES "\
                    f"('{session['user_id']}', '{session['customer_id']}',\
                        '{session['name']}', '{session['address1']}', '{session['address2']}',\
                        '{session['city']}', '{session['state']}', '{session['zipcode']}')"
        db = get_db()
        cursor = db.cursor()

        cursor.execute(command)

        db.commit()
        cursor.close()
    
        output_msg = 'Your profile has been saved!'

        return render_template('client_profile_mgmt.html', output_msg=output_msg)

    else:
        return render_template('client_profile_mgmt.html')



@app.route('/fuel_quote_form', methods=["POST", "GET"])
def fuel_quote_form():
    if request.method == "POST":
        gallons_requested = request.form['gallons_requested']
        # delivery_address = request.form['delivery_address']
        delivery_date = request.form['delivery_date']
        price_per_gallon = request.form['price_per_gallon']
        total_amount = request.form['total_amount']
    
        # print(gallons_requested, delivery_address, delivery_date)
        # print(price_per_gallon, total_amount)

        message = 'Your quotation request has been submitted!'

        return render_template('fuel_quote_form.html', message=message)

    else:
        command = f"SELECT address1, address2, city, state_,  zipcode \
                   FROM user_details WHERE customerid = '{session['customer_id']}';"
        db = get_db()
        cursor = db.cursor()

        cursor.execute(command)
        table_data = cursor.fetchone()
        # print(table_data)

        deli_address = ''
        for elem in table_data:
            if elem != '':
                if elem != table_data[-1]:
                    deli_address += elem + ', '
                else:
                    deli_address += elem

        db.commit()
        cursor.close()

        return render_template('fuel_quote_form.html', deli_address=deli_address)



@app.route('/fuel_quote_history')
def fuel_quote_history():
    return render_template('fuel_quote_history.html')

# wsgi_app = app.wsgi_app
if __name__ == "__main__":
    app.run()
