import unittest
import random
from flask import redirect

from sqlalchemy import false
from app import app, genID
from price_module import Pricing_module

from datetime import datetime

# To run: python test.py
# For coverage: coverage run test.py
# For coverage report: coverage report
# For coverage html: coverage html

# Another way of running: python test.py -v


class BasicTestCase(unittest.TestCase):
    
    # INDEX page
    # Test (Index page) whether index page is loading up
    def test_index(self):
        tester = app.test_client(self)

        response = tester.get('/', content_type='text/HTML')
        self.assertEqual(response.status_code, 200)
    
    # Test (Index page) whether logging in works
    def test_login(self):
        tester = app.test_client(self)

        data = dict(
            username="unittest",
            password="P@ssw0rd",
            login="Log in",
            log_txt="Log testing"
        )

        response = tester.post('/', data=data, follow_redirects=True)
        val = f"Welcome {data['username']}!"
        self.assertIn(str.encode(val), response.data)

    # Test (Index page) with no username & pwd
    def test_wo_username_password(self):
        tester = app.test_client(self)

        data = dict(
            username="",
            password="",
            login="Log in"
        )

        response = tester.post('/', data=data, follow_redirects=True)

        val = b"You need to enter both, username and password!"
        self.assertIn(val, response.data)

    # Test (Index page) with a username that doesn't exist
    def test_nonexistent_username(self):
        tester = app.test_client(self)

        data = dict(
            username="unittest_nonexistent",
            password="pwd",
            login="Log in"
        )

        response = tester.post('/', data=data, follow_redirects=True)

        val = b"This username doesn&#39;t exist!" # &#39; is '
        self.assertIn(val, response.data)

    # Test (Index page) with incorrect username and pwd
    def test_incorrect_username_pwd(self):
        tester = app.test_client(self)

        data = dict(
            username="unittest",
            password="pwd",
            login="Log in"
        )

        response = tester.post('/', data=data, follow_redirects=True)

        val = b"Incorrect username or password. Please try again!"
        self.assertIn(val, response.data)

    # Test (Index page) the sign up btn
    def test_signup_btn(self):
        tester = app.test_client(self)

        data = dict(
            signup="Sign up"
        )

        response = tester.post('/', data=data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


    #####################
    # SIGN UP Page
    def test_signup(self):
        tester = app.test_client(self)

        response = tester.get('/signup', content_type='text/HTML')
        self.assertEqual(response.status_code, 200)

    # Testing (Sign Up) register
    def test_signup_register(self):
        tester = app.test_client(self)
        response = ""

        while(True):
            random_num = int(random.random() * 1000000)
            uname = "unittest" + str(random_num)
            # print(uname)

            data = dict (
                username=uname,
                password="P@ssw0rd",
                register="Register"
            )   

            tester.set_cookie('localhost', 'username', uname)
            response = tester.post('/signup', data=data, follow_redirects=True)
            
            val = b"This username is already in use by another user."
            if val not in response.data:
                break

        self.assertEqual(response.status_code, 200)

    # Testing (Sign Up) back btn
    def test_signup_back(self):
        tester = app.test_client(self)

        data = dict(
            back="Back"
        )

        response = tester.post('/signup', data=data, follow_redirects=True)
        self.assertIn(b"Log in!", response.data)

    # Testing (Sign Up) Manage Profile btn
    def test_signup_manage_profile_btn(self):
        tester = app.test_client(self)

        data = dict(
            manage_profile="Manage Profile"
        )
        with tester.session_transaction() as sess:
                sess['username'] = 'ashutosh'
                sess['signed_in'] = True

        response = tester.post('/signup', data=data, follow_redirects=True)
        # print(response.data)
        self.assertIn(b"Profile Management", response.data)
    

    ###################
    # Home Page
    # Testing (home) for fuel quote form 
    def test_home_fuel_quote_form(self):
        tester = app.test_client(self)

        with tester.session_transaction() as sess:
            sess['customer_id'] = "AkAfegFX2b095o5D"

        things = dict(
            username="ashutosh",
            fuel_quote_form="Fuel Quote Form"
        )
        response = tester.post('/home',data=things, follow_redirects=False)
        self.assertEqual(response.status_code, 302) # 302 means it's been found

    # Testing (home) signout feature
    def test_home_signout(self):
        tester = app.test_client(self)

        things = dict(
            username="ashutosh",
            sign_out="Sign Out"
        )
        response = tester.post('/home',data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)



        
    #     # Testing for manage profile btn
    #     things = dict(
    #         username="ashutosh",
    #         manage_profile="Manage Profile"
    #     )
    #     response = tester.post('/home',data=things, follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)


    #     # Testing for fuel quote history
    #     things = dict(
    #         fuel_quote_history="Fuel Quote History"
    #     )
    #     response = tester.post('/home',data=things, follow_redirects=False)
    #     self.assertEqual(response.status_code, 302)

    #     # Test with None as table_data
    #     with tester.session_transaction() as sess:
    #         sess['customer_id'] = "somethingrandom"
    #     things = dict(
    #         fuel_quote_form="Fuel Quote Form"
    #     )
    #     response = tester.post('/home',data=things, follow_redirects=True)
    #     self.assertEqual(response.status_code, 200) 



    #######################
    # Client Profile Management
    # Testing (profile mgmt) get reponse
    def test_client_profile_mgmt(self):
        tester = app.test_client(self)
    
        response = tester.get('/client_profile_management')
        # self.assertEqual(response.status_code, 200)
        self.assertIn(b"Profile Management", response.data)

    # Testing (profile mgmt) with proper address
    def test_client_profile_mgmt_proper_addr(self):
        tester = app.test_client(self)
        things = dict(
            name="Ashutosh Kumar",
            address1="555 Side St",
            address2="",
            city="Houston",
            state="TX",
            zipcode="77007"
        )
        with tester.session_transaction() as sess:
            sess['username'] = "ashutosh"
        
        response = tester.post('/client_profile_management', data=things, follow_redirects=False)
        self.assertEqual(response.status_code, 200)

    # Testing (profile mgmt) with improper zipcode
    def test_client_profile_mgmt_improper_zipcode(self):
        tester = app.test_client(self)
        things = dict(
            name="Ashutosh Kumar",
            address1="555 Side St",
            address2="",
            city="Houston",
            state="TX",
            zipcode="770071"
        )
        with tester.session_transaction() as sess:
            sess['username'] = "ashutosh"
        
        response = tester.post('/client_profile_management', data=things, follow_redirects=False)
        self.assertIn(b"Zipcode must be 5 digits long!", response.data)

    # Testing (profile mgmt) with improper state
    def test_client_profile_mgmt_improper_state(self):
        tester = app.test_client(self)
        things = dict(
            name="Ashutosh Kumar",
            address1="555 Side St",
            address2="",
            city="Houston",
            state="-",
            zipcode="77007"
        )
        with tester.session_transaction() as sess:
            sess['username'] = "ashutosh"
        
        response = tester.post('/client_profile_management', data=things, follow_redirects=False)
        self.assertIn(b"You need to select a state!", response.data)



    #     # Testing home btn
        

    #     things = dict(
    #         home="Home"
    #     )
    #     response = tester.post('/client_profile_management', data=things, follow_redirects=False)
    #     self.assertEqual(response.status_code, 302)


    #     # Testing User exists but no previous address
    #     things = dict(
    #         name="Ashutosh Kumar",
    #         address1="555 Side St",
    #         address2="",
    #         city="Houston",
    #         state="TX",
    #         zipcode="77007"
    #     )
    #     with tester.session_transaction() as sess:
    #         sess['username'] = "nnnnnnnnnnnnnnnnnnnn"
        
    #     response = tester.post('/client_profile_management', data=things, follow_redirects=False)
    #     self.assertEqual(response.status_code, 200)



    # ######################
    # Fuel Quote Form

    # Testing (quote form) get response
    def test_fuel_quote_form(self):
        tester = app.test_client(self)
        with tester.session_transaction() as sess:
            sess['username'] = 'ashutosh'

        dt_str = "2030-05-01"
        things = dict(
                    gallons_request="1500",
                    delivery_date=dt_str
        )
        response = tester.get('/fuel_quote_form',
                    data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


        # Testing (quote form) home btn
    def test_fuel_quote_form_home_btn(self):
        tester = app.test_client(self)
        with tester.session_transaction() as sess:
            sess['username'] = 'ashutosh'
        things = dict(
                    gallons_request="1500",
                    delivery_date="2030-05-05",
                    home="Home"
        )
        response = tester.post('/fuel_quote_form', data=things, follow_redirects=True)
        self.assertIn(b"Home", response.data)


    # Testing (quote form) the whole form
    def test_fuel_quote_form_entire_form(self):
        tester = app.test_client(self)

        things = dict(
                    gallons_requested="1500",
                    delivery_date="2030-05-29",
                    log_txt="logging testing",
                    calculate="Calculate",
                    today="2022-04-30"
        )
        with tester.session_transaction() as sess:
            sess['username'] = "ashutosh"
            sess['customer_id'] = "AkAfegFX2b095o5D"
            sess['deli_date'] = "2030-05-29"
            sess['hist'] = 'no'
        
        response = tester.post('/fuel_quote_form', data=things, follow_redirects=True)
        self.assertIn(b"Fuel Quote Confirmation", response.data)
        # self.assertEqual(response.status_code, 302)


    # Testing (quote form) with the delivery date in the past
    def test_fuel_quote_form_deli_date_past(self):
        tester = app.test_client(self)
        things = dict(
                    gallons_requested="1500",
                    delivery_date="2020-05-29",
                    log_txt="logging testing",
                    calculate="Calculate",
                    today="2022-04-30"
        )
        with tester.session_transaction() as sess:
            sess['username'] = "ashutosh"
            sess['customer_id'] = "AkAfegFX2b095o5D"
            sess['deli_date'] = "2030-05-29"
            sess['hist'] = 'no'
        
        response = tester.post('/fuel_quote_form', data=things, follow_redirects=True)
        self.assertIn(b"The delivery date cannot be in the past!", response.data)

    ######################
    # Fuel Quote Confirm

    # Testing (confirm) get response
    def test_fuel_quote_confirm(self):
        tester = app.test_client(self)
        price_p_gallon = 1.71

        with tester.session_transaction() as sess:
            sess['price_p_gallon'] = price_p_gallon
            sess['total_price'] = 1.71 * 1500
            sess['username']="ashutosh",
            sess['customer_id']="AkAfegFX2b095o5D"

        response = tester.get('/fuel_quote_confirm', follow_redirects=True)
        val = str.encode(f"Price per gallon = ${price_p_gallon}")
        self.assertIn(val, response.data)

    # Testing (confirm) submit conditional
    def test_fuel_quote_confirm_submit(self):
        tester = app.test_client(self)

        things = dict(
            submit="Submit",
            log_txt="log testing"
        )
        with tester.session_transaction() as sess:
            sess['order_id'] = "TESTINGID"
            sess['customer_id'] = "AFFneHeRLBXoRpxe"
            sess['deli_address'] = "Random Address"
            sess['gallons_req'] = "1500"
            sess['deli_date'] = "2030-05-29"
            sess['price_p_gallon'] = 1.71
            sess['total_price'] = 2000

        response = tester.post('/fuel_quote_confirm', data=things, follow_redirects=True)
        self.assertIn(b"Order successfully submitted!", response.data)
    

    #     # Testing Home conditional
    #     things = dict(
    #         home="Home"
    #     )

    #     response = tester.post('/fuel_quote_confirm', data=things, follow_redirects=True)
    #     self.assertEqual(response.status_code, 200)

    

    
    #######################
    # Fuel Quote History
    # Testing (history) get response
    def test_fuel_quote_hist(self):
        tester = app.test_client(self)
        with tester.session_transaction() as sess:
            sess['username'] = 'ashutosh'

        response = tester.get('/fuel_quote_history', content_type='/fuel_quote_history',
            follow_redirects=True)
        self.assertIn(b"Quotation History", response.data)

    # Testing (history) post response
    def test_fuel_quote_hist_home_btn(self):
        tester = app.test_client(self)
        with tester.session_transaction() as sess:
            sess['username'] = 'ashutosh'

        things = dict(home="Home")

        response = tester.post('/fuel_quote_history',data=things, follow_redirects=True)
        self.assertIn(b"Home", response.data)        

    
    # TEST Price_module
    def test_price_module(self):
        pm = Pricing_module()
        actual = pm.calcPrice('TX', 'yes', 1500)
        expected = 1.695

        self.assertEqual(actual, expected)


    # TEST genId
    def test_gen_ID(self):
        actual = genID(16)
    
        
if __name__ == '__main__':
    unittest.main()