from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/client_profile_management')
def client_profile_management():
    return render_template('client_profile_mgmt.html')

@app.route('/fuel_quote_form')
def fuel_quote_form():
    return render_template('fuel_quote_form.html')

@app.route('/fuel_quote_history')
def fuel_quote_history():
    return render_template('fuel_quote_history.html')


if __name__ == "__main__":
    app.run()
