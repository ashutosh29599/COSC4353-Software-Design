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


# Testing Pricing Module! Works!
# price = price_module.Pricing_module().calcPrice('tx', 'no', 1500)
# print(f'The price per gallon is ${price}!')
# print(f'Total amount: 1500 * {price} = ${1500 * price:.2f}!')



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
    # session['signed_in'] = False
    if request.method == "POST":
        if request.form.get('login') == 'Log in':
            username = request.form.get('username')
            password = request.form.get('password')

            if username == "" or password == "":
                return redirect(url_for("index"))

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
                session['username'] = username

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

        elif request.form.get('sign_out') == 'Sign Out':
            # if not session['signed_in']:
            output_msg = "You are not signed in!"
            # if 'signed_in' in request.cookies:
            #     print('hola')
            if session['signed_in']:
                output_msg = "Successfully signed out!"
                session['signed_in'] = False
            flash(output_msg, 'error')
            return redirect(url_for("index"))
                

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

        elif request.form.get('fuel_quote_form') == 'Fuel Quote Form':
            return redirect(url_for("fuel_quote_form"))

    return render_template('logged_in.html')

@app.route('/client_profile_management', methods=["POST", "GET"])
def client_profile_management():
    if request.method == "POST":
        if request.form.get('home') == 'Home':
            return redirect(url_for("logged_in"))


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
        if request.form.get('home') == 'Home':
            return redirect(url_for("logged_in"))


        #TODO: FIX THIS
        if request.form.get('submit') == 'Submit':
            out_msg = 'Your quotation request has been submitted!'
            return render_template('fuel_quote_form.html', out_msg=out_msg)

   

        gallons_requested = request.form['gallons_requested']
        # delivery_address = request.form['delivery_address']
        delivery_date = request.form['delivery_date']
        # price_per_gallon = request.form['price_per_gallon']
        # total_amount = request.form['total_amount']

        session['gallons_req'] = gallons_requested
        session['deli_date'] = delivery_date
    
        # print(gallons_requested, delivery_address, delivery_date)
        # print(price_per_gallon, total_amount)

        # TODO: Update session_hist here by checking
        # Check the table orders for the user id
        # Get the userid from the username
        command = f"SELECT customerid\
                    FROM customer\
                    WHERE username = '{session['username']}';"
        
        db = get_db()
        cursor = db.cursor()

        cursor.execute(command)
        session['customer_id'] = cursor.fetchone()[0]

        command = f"SELECT orderid\
                     FROM orders\
                     WHERE customerid = '{session['customer_id']}';" 
        cursor.execute(command)
        num_orders = len(cursor.fetchall())

        if num_orders == 0:
            session['hist'] = 'no'
        else:
            session['hist'] = 'yes'
    
        cursor.close()

        price_p_gal = price_module.Pricing_module().calcPrice(session['state'],\
                        session['hist'], gallons_requested)
        total_price = price_p_gal * float(gallons_requested)

        message = [f'Price per gallon = ${price_p_gal:.2f}', f'Total amount = ${total_price:.2f}']


        if request.form.get('calculate') == 'Calculate':
            return render_template('fuel_quote_form.html', message=message)
        elif request.form.get('submit') == 'Submit':
            print('hol')
            out_msg = 'Your quotation request has been submitted!'
            return render_template('fuel_quote_form.html', out_msg=out_msg)
        
    else:
        command = f"SELECT customerid\
                    FROM customer\
                    WHERE username = '{session['username']}';"
        
        db = get_db()
        cursor = db.cursor()

        cursor.execute(command)
        session['customer_id'] = cursor.fetchone()[0]

        command = f"SELECT address1, address2, city, state_,  zipcode \
                   FROM user_details WHERE customerid = '{session['customer_id']}';"

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



@app.route('/fuel_quote_history', methods=["POST", "GET"])
def fuel_quote_history():
    if request.form.get('home') == 'Home':
            return redirect(url_for("logged_in"))

    return render_template('fuel_quote_history.html')

# wsgi_app = app.wsgi_app
if __name__ == "__main__":
    app.run()
