from collections import UserDict
# from crypt import methods
from threading import get_ident
from flask import Flask, render_template, request, url_for, g, session, redirect, flash
from sqlalchemy import outerjoin
import price_module
from datetime import datetime

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


def log(user, text):
    if user == "":
        return
    
    curr_timestamp = str(datetime.now())
    curr_timestamp += ':'
    

    filename = 'SQL Log/' + user + '.txt'

    with open(filename, 'a') as file:
        print(curr_timestamp, file=file)
        print(text, file=file)



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
            temp = " ".join(command.split()) + '\n'
            log_txt = temp

            db = get_db()
            cursor = db.cursor()
            cursor.execute(command)
            table_data = cursor.fetchone()  # table_data[0] is the pwd hash
            cursor.close()

            if table_data == None:
                output_msg = "This username doesn't exist!"
                flash(output_msg, 'error')
                return redirect(url_for('index'))

            if not bcrypt.check_password_hash(table_data[0], password): # incorrect username or pwd
                output_msg = "Incorrect username or password. Please try again!"
                flash(output_msg, 'error')
                return redirect(url_for("index"))

            else:   # correct username and pwd
                session['signed_in'] = True
                session['username'] = username

                # Set customer_id in the cookie
                command = f"SELECT customerid\
                            FROM customer\
                            WHERE username = '{session['username']}';"
                temp = " ".join(command.split()) + '\n'
                log_txt += temp

                db = get_db()
                cursor = db.cursor()

                cursor.execute(command)
                session['customer_id'] = cursor.fetchone()[0]
                cursor.close()

                # # log_txt += '\n'
                log(session['customer_id'], log_txt)

                return redirect(url_for('logged_in'))

            # return render_template('index.html')
            # return redirect(url_for("index"))
        
        elif request.form.get('signup') == 'Sign up':
            return redirect(url_for("signup"))

        # elif request.form.get('manage_profile') == 'Manage Profile':
        #     if not session['signed_in']:
        #         output_msg = "You must sign in or sign up before you can manage your profile."
        #         flash(output_msg, 'error')
        #         return redirect(url_for("index"))

        #     return redirect(url_for("client_profile_management"))

        # elif request.form.get('sign_out') == 'Sign Out':
        #     # if not session['signed_in']:
        #     output_msg = "You are not signed in!"
        #     # if 'signed_in' in request.cookies:
        #     #     print('hola')
        #     if session['signed_in']:
        #         output_msg = "Successfully signed out!"
        #         session['signed_in'] = False
        #     flash(output_msg, 'error')
        #     return redirect(url_for("index"))
                

    else: # method == GET
        return render_template('index.html')

@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        if request.form.get('register') == 'Register':
            session['username'] = request.form.get('username')
            encrypted_pwd = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
            session['password'] = encrypted_pwd

            # session['username'] = username
            # session['password']
            
            db = get_db()
            cursor = db.cursor()

            # Check username for duplicates
            command = f"SELECT * FROM customer \
                        WHERE username = '{session['username']}';"
            temp = " ".join(command.split()) + '\n'
            log_txt = temp
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
            temp = " ".join(command.split()) + '\n'
            log_txt += temp

            cursor.execute(command)
            db.commit()
            cursor.close()

            # output_msg = "You've successfully signed up! You now need to login\
            #         to complete your profile info before you can request a quote."
            # flash(output_msg, 'success')

            session['signed_in'] = True

            # log_txt += '\n'
            log(session['customer_id'], log_txt)

            return redirect(url_for('logged_in'))

        elif request.form.get('back') == 'Back':
            return redirect(url_for('index'))

        elif request.form.get('manage_profile') == 'Manage Profile':
            if not session['signed_in']:
                output_msg = "You must sign in or sign up before you can manage your profile."
                flash(output_msg, 'error')
                return redirect(url_for("signup"))

            return redirect(url_for("client_profile_management"))

    return render_template('signup.html')


@app.route('/home', methods=["POST", "GET"])
def logged_in():
    # output_msg = "You've successfully logged in! You will now need to \
    #             complete your profile if you haven't done so before you can request a quote!"
    # flash(output_msg, 'error')

    if request.method == "POST":
        if request.form.get('manage_profile') == 'Manage Profile':
            return redirect(url_for("client_profile_management"))
        
        # elif request.form.get('fuel_quote_form') == 'Fuel Quote Form':
        #     return redirect(url_for("fuel_quote_form"))

        elif request.form.get('fuel_quote_history') == 'Fuel Quote History':
            return redirect(url_for("fuel_quote_history"))

        elif request.form.get('fuel_quote_form') == 'Fuel Quote Form':
            # Check if the user has updated the address in the db
            db = get_db()
            cursor = db.cursor()
            command = f"SELECT address1, address2, city, state_,  zipcode \
                   FROM user_details WHERE customerid = '{session['customer_id']}';"
            temp = " ".join(command.split()) + '\n'
            log_txt = temp

            cursor.execute(command)
            table_data = cursor.fetchone()
            # print(table_data)
            
            # command = f"SELECT customerid\
            #                 FROM customer\
            #                 WHERE username = '{session['username']}';"
            # temp = " ".join(command.split()) + '\n'
            # log_txt += temp

            # cursor.execute(command)
            # session['customer_id'] = cursor.fetchone()[0]
            cursor.close()

            # log_txt += '\n'
            log(session['customer_id'], log_txt)

            if table_data == None: # No address in db
                output_msg = "Please update your address in your account."
                flash(output_msg, 'error')
                return redirect(url_for('logged_in'))

            return redirect(url_for("fuel_quote_form"))

        elif request.form.get('sign_out') == 'Sign Out':
            session['signed_in'] = False
            session['username'] = ''
            session['password'] = ''
            
            return redirect(url_for('index'))

    if session['username'] == '':
        return render_template('logged_in.html')

    return render_template('logged_in.html', uname=session['username'])

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

        # Check if the username exists -- i.e. check if the user is updating his address
        db = get_db()
        cursor = db.cursor()
        command = f"SELECT customerid\
                    FROM customer\
                    WHERE username = '{session['username']}';"
        temp = " ".join(command.split()) + '\n'
        log_txt = temp
        
        cursor.execute(command)
        data = cursor.fetchone() # user customerid

        if len(data) != 0: # user already exists
            command = f"SELECT COUNT(*) FROM user_details\
                        WHERE customerid = '{data[0]}';"
            temp = " ".join(command.split()) + '\n'
            log_txt += temp

            cursor.execute(command)
            num = cursor.fetchall()[0][0]
            print(num)

            if num == 0: # No previous address
                session['user_id'] = genID(16)
                command = "INSERT INTO user_details VALUES "\
                            f"('{session['user_id']}', '{session['customer_id']}',\
                                '{session['name']}', '{session['address1']}', '{session['address2']}',\
                                '{session['city']}', '{session['state']}', '{session['zipcode']}')"
                temp = " ".join(command.split()) + '\n'
                log_txt += temp

                output_msg = 'Your profile has been saved!'
            
            else:
                command = f"UPDATE user_details SET\
                            cust_name = '{session['name']}', address1 = '{session['address1']}', address2 = '{session['address2']}',\
                            city = '{session['city']}', state_ = '{session['state']}', zipcode = '{session['zipcode']}'\
                            WHERE customerid = '{data[0]}';"
                temp = " ".join(command.split()) + '\n'
                log_txt += temp

                output_msg = 'Your profile have been updated!'
            # print(command)

        cursor.execute(command)
        db.commit()
    
        # Get customer id into cookies
        command = f"SELECT customerid\
                            FROM customer\
                            WHERE username = '{session['username']}';"
        temp = " ".join(command.split()) + '\n'
        log_txt += temp
        cursor.execute(command)
        session['customer_id'] = cursor.fetchone()[0]
        cursor.close()

        # log_txt += '\n'
        log(session['customer_id'], log_txt)
        
        return render_template('client_profile_mgmt.html', output_msg=output_msg)

    else:
        return render_template('client_profile_mgmt.html')



@app.route('/fuel_quote_form', methods=["POST", "GET"])
def fuel_quote_form():
    if request.method == "POST":
        if request.form.get('home') == 'Home':
            return redirect(url_for("logged_in"))

        gallons_requested = request.form['gallons_requested']
        delivery_date = request.form['delivery_date']
        # print(type(delivery_date))
        # print(delivery_date)

        today = datetime.today().strftime('%Y-%m-%d')
        if today > delivery_date:   # the date is in the past
            out_msg = 'The delivery date cannot be in the past!'
            flash(out_msg, 'error')
            return redirect(url_for('fuel_quote_form'))

        session['gallons_req'] = gallons_requested
        session['deli_date'] = delivery_date
    
        # Check the table orders for the user id
        # Get the userid from the username
        command = f"SELECT customerid\
                    FROM customer\
                    WHERE username = '{session['username']}';"
        temp = " ".join(command.split()) + '\n'
        log_txt = temp
        
        db = get_db()
        cursor = db.cursor()

        cursor.execute(command)
        session['customer_id'] = cursor.fetchone()[0]

        command = f"SELECT orderid\
                     FROM orders\
                     WHERE customerid = '{session['customer_id']}';"
        temp = " ".join(command.split()) + '\n'
        log_txt += temp

        cursor.execute(command)
        num_orders = len(cursor.fetchall())

        if num_orders == 0:
            session['hist'] = 'no'
        else:
            session['hist'] = 'yes'

        # Get the state in the cookies
        command = f"SELECT state_\
                    FROM user_details\
                    WHERE customerid = '{session['customer_id']}';"
        temp = " ".join(command.split()) + '\n'
        log_txt += temp
            
        cursor.execute(command)
        session['state'] = cursor.fetchone()[0]
        cursor.close()

        price_p_gal = price_module.Pricing_module().calcPrice(session['state'],\
                        session['hist'], gallons_requested)
        total_price = price_p_gal * float(gallons_requested)

        session['price_p_gallon'] = price_p_gal
        session['total_price'] = total_price

        # log_txt += '\n'
        log(session['customer_id'], log_txt)

        if request.form.get('calculate') == 'Calculate':
            return redirect('fuel_quote_confirm')
            # return render_template('fuel_quote_confirm.html', message=message)
        
    else:
        command = f"SELECT customerid\
                    FROM customer\
                    WHERE username = '{session['username']}';"
        temp = " ".join(command.split()) + '\n'
        log_txt = temp
        
        db = get_db()
        cursor = db.cursor()

        cursor.execute(command)
        session['customer_id'] = cursor.fetchone()[0]

        command = f"SELECT address1, address2, city, state_,  zipcode \
                   FROM user_details WHERE customerid = '{session['customer_id']}';"
        temp = " ".join(command.split()) + '\n'
        log_txt += temp

        cursor.execute(command)
        table_data = cursor.fetchone()

        deli_address = ''
        for elem in table_data:
            if elem != '':
                if elem != table_data[-1]:
                    deli_address += elem + ', '
                else:
                    deli_address += elem
        session['deli_addess'] = deli_address

        db.commit()
        cursor.close()

        # log_txt += '\n'
        log(session['customer_id'], log_txt)

        return render_template('fuel_quote_form.html', deli_address=deli_address)



@app.route('/fuel_quote_confirm', methods=["POST", "GET"])
def fuel_quote_confirm():
    if request.method == "POST":
        if request.form.get('home') == 'Home':
            return redirect(url_for("logged_in"))
        
        elif request.form.get('submit') == 'Submit': # store the order in the db
            # create a unique order id
            session['order_id'] = genID(16)

            # Getting Delivery address from the db
            db = get_db()
            cursor = db.cursor()
            command = f"SELECT address1, address2, city, state_,  zipcode \
                   FROM user_details WHERE customerid = '{session['customer_id']}';"
            temp = " ".join(command.split()) + '\n'
            log_txt = temp
        
            cursor.execute(command)
            table_data = cursor.fetchone()
            # print(table_data)
            # print(table_data)

            deli_address = ''
            for elem in table_data:
                if elem != '':
                    if elem != table_data[-1]:
                        deli_address += elem + ', '
                    else:
                        deli_address += elem
            session['deli_address'] = deli_address
            # print(session['deli_address'])

            try:
                command = f"INSERT INTO orders\
                        (orderid, customerid, custlocation, gallonsrequested, dateofrequest, deliverydate, price_p_gal, price)\
                        VALUES ('{session['order_id']}', '{session['customer_id']}',\
                            '{session['deli_address']}', {session['gallons_req']}, NOW(),\
                            '{session['deli_date']}', {session['price_p_gallon']}, {session['total_price']});"
                temp = " ".join(command.split()) + '\n'
                log_txt += temp
                
                db = get_db()
                cursor = db.cursor()

                cursor.execute(command)
                db.commit()

                out_msg = 'Order successfully submitted!'

                # log_txt += '\n'
                log(session['customer_id'], log_txt)

            except:
                out_msg = 'Unexpected error!'

            # return render_template('fuel_quote_confirm.html', out_msg=out_msg)
            return render_template('fuel_quote_success.html', out_msg=out_msg)

    price_p_gal = session['price_p_gallon']
    total_price = session['total_price']
    
    message = [f'Price per gallon = ${price_p_gal:,.2f}', f'Total amount = ${total_price:,.2f}']
    return render_template('fuel_quote_confirm.html', message=message)



@app.route('/fuel_quote_history', methods=["POST", "GET"])
def fuel_quote_history():
    if request.method == "POST":
        if request.form.get('home') == 'Home':
            return redirect(url_for("logged_in"))

    # Get customer id to the cookie
    command = f"SELECT customerid\
                    FROM customer\
                    WHERE username = '{session['username']}';"
    temp = " ".join(command.split()) + '\n'
    log_txt = temp
    
    db = get_db()
    cursor = db.cursor()

    cursor.execute(command)
    session['customer_id'] = cursor.fetchone()[0]

    # Get the history from the db
    command = f"SELECT\
                dateofrequest, deliverydate, gallonsrequested, custlocation, price_p_gal, price\
                FROM orders\
                WHERE customerid = '{session['customer_id']}';"
    temp = " ".join(command.split()) + '\n'
    log_txt += temp
    
    cursor.execute(command)
    data = cursor.fetchall()
    # print(datetime.date(data[0][0]))    


    cursor.close()

    # log_txt += '\n'
    log(session['customer_id'], log_txt)
    

    return render_template('fuel_quote_history.html', data=data)

# wsgi_app = app.wsgi_app
if __name__ == "__main__":
    app.run()
