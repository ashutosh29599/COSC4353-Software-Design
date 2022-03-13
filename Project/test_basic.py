import unittest
from app import app

class BasicTestCase(unittest.TestCase):
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='/')
        self.assertEqual(response.status_code, 200)

    
    def test_signup(self):
        tester = app.test_client(self)
        response = tester.get('/signup', content_type='/signup')
        self.assertEqual(response.status_code, 200)



    def test_client_profile_mgmt(self):
        tester = app.test_client(self)
        response = tester.get('/client_profile_management', content_type='/client_profile_management')
        self.assertEqual(response.status_code, 200)

    def test_fuel_quote_form(self):
        tester = app.test_client(self)
        response = tester.get('/fuel_quote_form', content_type='/fuel_quote_form')
        self.assertEqual(response.status_code, 200)

    def test_fuel_quote_hist(self):
        tester = app.test_client(self)
        response = tester.get('/fuel_quote_history', content_type='/fuel_quote_history')
        self.assertEqual(response.status_code, 200)



    # def test_other(self):
    #     tester = app.test_client(self)
    #     response = tester.get('a', content_type='html/text')
    #     self.assertEqual(response.status_code, 404)
    #     self.assertTrue(b'does not exist' in response.data)
        
if __name__ == '__main__':
    unittest.main()