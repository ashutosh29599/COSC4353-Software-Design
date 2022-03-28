from collections import UserDict
from threading import get_ident
from flask import Flask, render_template, request, url_for, g, session, redirect, flash
import price_module

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
import random, string

# from wtforms import Form, BooleanField, StringField, PasswordField, validators


app = Flask(__name__)
app.secret_key ="123"


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
    if request.method == "POST":
        if request.form.get('login') == 'Log in':
            username = request.form.get('username')
            password = request.form.get('password')

            # return render_template('index.html')
            return redirect(url_for("index"))
        
        elif request.form.get('signup') == 'Sign up':
            return redirect(url_for("signup"))

        elif request.form.get('manage_profile') == 'Manage Profile':
            return redirect(url_for("client_profile_management"))

    else: # method == GET
        return render_template('index.html')

@app.route('/signup', methods=["POST", "GET"])
def signup():
        
    if request.method == "POST":
        if request.form.get('register') == 'Register':
            session['username'] = request.form.get('username')
            session['password'] = request.form.get('password')
            output_msg = "You've successfully signed up! You now need to login\
                    to complete your profile info before you can request a quote."


            session['customer_id'] = genID(16)
            command = "INSERT INTO customer VALUES "\
                      f"('{session['customer_id']}', '' , '{session['username']}', '{session['password']}')"
            db = get_db()
            cursor = db.cursor()

            cursor.execute(command)

            db.commit()
            cursor.close()
            
            flash(output_msg)
            return render_template('signup.html')

        elif request.form.get('back') == 'Back':
            # return redirect(url_for("index"))
            return redirect(url_for('index'))

        elif request.form.get('manage_profile') == 'Manage Profile':
            return redirect(url_for("client_profile_management"))

    # if request.form['back'] == 'Back':
    #     return redirect(url_for("index"))
            

    return render_template('signup.html')


@app.route('/client_profile_management', methods=["POST", "GET"])
def client_profile_management():
    if request.method == "POST":
        session['name'] = request.form['name']
        session['address1'] = request.form['address1']
        session['address2'] = request.form['address2']
        session['city'] = request.form['city']
        session['state'] = request.form.get('state')
        session['zipcode'] = request.form['zipcode']
    
        # Zipcode should be 5 digits long
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



        # print(name, address1, address2, city, state, zipcode)
    
        #TODO: send the data to the db
        


        output_msg = 'Your profile has been saved!'

        return render_template('client_profile_mgmt.html', output_msg=output_msg)

    else:
        return render_template('client_profile_mgmt.html')



@app.route('/fuel_quote_form', methods=["POST", "GET"])
def fuel_quote_form():
    if request.method == "POST":
        gallons_requested = request.form['gallons_requested']
        delivery_address = request.form['delivery_address']
        delivery_date = request.form['delivery_date']
        price_per_gallon = request.form['price_per_gallon']
        total_amount = request.form['total_amount']
    
        # print(gallons_requested, delivery_address, delivery_date)
        # print(price_per_gallon, total_amount)
        message = 'Your quotation request has been submitted!'

        return render_template('fuel_quote_form.html', message=message)

    else:
        return render_template('fuel_quote_form.html')



@app.route('/fuel_quote_history')
def fuel_quote_history():
    return render_template('fuel_quote_history.html')

# wsgi_app = app.wsgi_app
if __name__ == "__main__":
    app.run()
