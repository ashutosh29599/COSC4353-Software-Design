import unittest

from sqlalchemy import false
from app import app, genID
from price_module import Pricing_module

from datetime import datetime

# To run: python test.py
# For coverage: coverage run test.py
# For coverage report: coverage report


class BasicTestCase(unittest.TestCase):
    # INDEX
    def test_index(self):
        tester = app.test_client(self)

        # Testing get reponse and sign in
        things = dict(
                username="ashutosh",
                password="pwd",
                login="Log in",
                log_txt="log testing"
        )

        response = tester.get('/', content_type='/', follow_redirects=True, data=things)
        self.assertEqual(response.status_code, 200)

        response = tester.post('/', data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Testing sign up
        things = dict(
                username="ashutosh",
                password="pwd",
                signup="Sign up",
                log_txt="log testing"
        )
        response = tester.post('/', data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


        # Testing with no username and password
        things = dict(
                username="",
                password="",
                login="Log in",
                log_txt="log testing"
        )
        response = tester.post('/', data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


        # Testing with incorrect username and password
        things = dict(
                username="ashutosh",
                password="hahahahahah",
                login="Log in",
                log_txt="log testing"
        )
        response = tester.post('/', data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


        # Testing with None as table data
        things = dict(
                username="this_username_doesnt_exist_testing_only",
                password="pwd",
                login="Log in",
                log_txt="log testing"
            )
        response = tester.post('/', data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


    # SIGN UP  -- Incomplete
    def test_signup(self):
        tester = app.test_client(self)

        # with tester.session_transaction() as sess:
        #     sess['username'] = "ashutosh",
            # sess['customer_id']="AkAfegFX2b095o5D"

        # Get response
        response = tester.get('/signup', content_type='/signup')
        self.assertEqual(response.status_code, 200)


        # Register
        things = dict(
                username="ashutosh",
                password="pwd",
                log_txt="log testing",
                register="Register"
            )
        response = tester.post('/signup', data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


        # if table_data = 0
        things = dict(
                username="nnnnnnnnnnnnnnnnnn12",
                password="pwd",
                log_txt="log testing",
                register="Register"
            )
        # with tester.session_transaction() as sess:
        #     sess['username'] = "somethingthatdoesnotexist"
        response = tester.post('/signup', data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


        # Back conditional
        things = dict(
                username="ashutosh",
                password="pwd",
                log_txt="log testing",
                back="Back"
            )
        response = tester.post('/signup', data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Manage Profile conditional
        with tester.session_transaction() as sess:
            sess['signed_in'] = False

        things = dict(
                username="ashutosh",
                password="pwd",
                log_txt="log testing",
                # signed_in=False,
                manage_profile="Manage Profile"
            )
        response = tester.post('/signup', data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        with tester.session_transaction() as sess:
            sess['signed_in'] = True

        response = tester.post('/signup', data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)



    ##################
    # Home Page
    def test_home(self):
        tester = app.test_client(self)
        
        # Testing for manage profile btn
        things = dict(
            username="ashutosh",
            manage_profile="Manage Profile"
        )
        response = tester.post('/home',data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


        # Testing for fuel quote history
        things = dict(
            fuel_quote_history="Fuel Quote History"
        )
        response = tester.post('/home',data=things, follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        # Testing for sign out
        things = dict(
            username="ashutosh",
            sign_out="Sign Out"
        )
        response = tester.post('/home',data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = tester.get('/home', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Testing for fuel quote form
        with tester.session_transaction() as sess:
            sess['customer_id'] = "AkAfegFX2b095o5D"

        things = dict(
            username="ashutosh",
            fuel_quote_form="Fuel Quote Form"
        )
        response = tester.post('/home',data=things, follow_redirects=False)
        self.assertEqual(response.status_code, 302) # 302 means it's been found

        # Test with None as table_data
        with tester.session_transaction() as sess:
            sess['customer_id'] = "somethingrandom"
        things = dict(
            fuel_quote_form="Fuel Quote Form"
        )
        response = tester.post('/home',data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200) 



    #######################
    # Client Profile Management
    def test_client_profile_mgmt(self):
        tester = app.test_client(self)
        things = dict(
            name="Ashutosh Kumar",
            address1="555 Side St",
            address2="",
            city="Houston",
            state="TX",
            zipcode="77007"
        )
        
        # Testing get response
        response = tester.get('/client_profile_management',data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Testing home btn
        

        things = dict(
            home="Home"
        )
        response = tester.post('/client_profile_management', data=things, follow_redirects=False)
        self.assertEqual(response.status_code, 302)


        # Testing with correct address
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

        # Testing with improper zipcode
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
        self.assertEqual(response.status_code, 200)

        # Testing with improper state
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
        self.assertEqual(response.status_code, 200)

        # Testing User exists but no previous address
        things = dict(
            name="Ashutosh Kumar",
            address1="555 Side St",
            address2="",
            city="Houston",
            state="TX",
            zipcode="77007"
        )
        with tester.session_transaction() as sess:
            sess['username'] = "nnnnnnnnnnnnnnnnnnnn"
        
        response = tester.post('/client_profile_management', data=things, follow_redirects=False)
        self.assertEqual(response.status_code, 200)



    ######################
    # Fuel Quote Form

    def test_fuel_quote_form(self):
        tester = app.test_client(self)
        with tester.session_transaction() as sess:
            sess['username'] = 'ashutosh'

        dt_str = "2030-05-01"
        # dt = datetime.strptime(dt_str, "%Y-%m-%d")
        # dt = (dt.date())


        # Testing get reponse
        things = dict(
                    gallons_request="1500",
                    delivery_date=dt_str
        )
        response = tester.get('/fuel_quote_form',
                    data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


        # Testing home
        things = dict(
                    gallons_request="1500",
                    delivery_date="2030-05-05",
                    home="Home"
        )
        response = tester.post('/fuel_quote_form', data=things, follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        # Testing the whole form
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
        
        response = tester.post('/fuel_quote_form', data=things, follow_redirects=False)
        self.assertEqual(response.status_code, 302)

        # Testing with the delivery date in the past
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
        
        response = tester.post('/fuel_quote_form', data=things, follow_redirects=False)
        self.assertEqual(response.status_code, 302)


    ######################
    # Fuel Quote Confirm

    def test_fuel_quote_confirm(self):
        tester = app.test_client(self)

        with tester.session_transaction() as sess:
            sess['price_p_gallon'] = 1.71
            sess['total_price'] = 1.71 * 1500
            sess['username']="ashutosh",
            sess['customer_id']="AkAfegFX2b095o5D"

        response = tester.get('/fuel_quote_confirm', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Testing Home conditional
        things = dict(
            home="Home"
        )

        response = tester.post('/fuel_quote_confirm', data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Testing submit conditional
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
        self.assertEqual(response.status_code, 200)

    
    #######################
    # Fuel Quote History
    def test_fuel_quote_hist(self):
        tester = app.test_client(self)
        with tester.session_transaction() as sess:
            sess['username'] = 'ashutosh'

        response = tester.get('/fuel_quote_history', content_type='/fuel_quote_history',
            follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Testing port response
        things = dict(home="Home")
        response = tester.post('/fuel_quote_history',data=things, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    
    # TEST Price_module
    def test_price_module(self):
        pm = Pricing_module()
        actual = pm.calcPrice('TX', 'yes', 1500)
        expected = 1.695

        self.assertEqual(actual, expected)


    # TEST genId
    def test_gen_ID(self):
        actual =genID(16)
        

    
        
if __name__ == '__main__':
    unittest.main()