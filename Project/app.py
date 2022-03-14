from flask import Flask, render_template, request, url_for, session, redirect, flash
import price_module


app = Flask(__name__)
app.secret_key ="123"

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == "POST":
        if request.form['login'] == 'Log in':
            username = request.form.get('username')
            password = request.form.get('password')
            return render_template('index.html')
        
        elif request.form['signup'] == 'Sign up':
            return redirect(url_for(signup))
        

    else: # method == GET
        return render_template('index.html')

@app.route('/signup', methods=["POST", "GET"])
def signup():
        
    if request.method == "POST":
        if request.form['register'] == 'Register':
            username = request.form.get('username')
            password = request.form.get('password')
            output_msg = "You've successfully signed up! You now need to login\
                    to complete your profile info before you can request a quote."
            
            flash(output_msg)
            return render_template('signup.html')

    # if request.form['back'] == 'Back':
    #     return redirect(url_for("index"))
            

    return render_template('signup.html')


@app.route('/client_profile_management', methods=["POST", "GET"])
def client_profile_management():
    if request.method == "POST":
        fname = request.form['fname']
        address1 = request.form['address1']
        address2 = request.form['address2']
        city = request.form['city']
        state = request.form.get('state')
        zipcode = request.form['zipcode']
    
        print(state)
        # Zipcode should be 5 digits long
        zip_count = 0
        for _ in zipcode:
            zip_count += 1
        if zip_count != 5:
            flash("Zipcode must be 5 digits long!")
            return render_template('client_profile_mgmt.html',\
                                    fname=fname, address1=address1,\
                                    address2=address2, city=city, state=state)
        
        # State needs to be selected
        if state == "-":
            flash("You need to select a state!")
            return render_template('client_profile_mgmt.html',\
                                    fname=fname, address1=address1,\
                                    address2=address2, city=city, zipcode=zipcode)

        # print(fname, address1, address2, city, state, zipcode)
    
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
    app.run(debug=True)
