import os
import flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):
    
    def setUp(self):
        self.db_fd, flaskr.app.config['DB_NAME'] = tempfile.mkstemp()
        flaskr.app.config['TESTING'] = True
        self.app = flaskr.app.test_client()
        flaskr.init_db()
    
    def tearDown(self):
        os.unlink(flaskr.app.config['DB_NAME'])
        
    def test_admin_created(self):
        user = flaskr.Users.select(flaskr.Users.q.email==flaskr.app.config['ADMIN_USERNAME'])[0]
        assert user.email == flaskr.app.config['ADMIN_USERNAME']

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
    
    def make_good_post(self):
        return self.app.post('/add', data=dict(
            title='this is a good post',
            body="yessss",
            post_on="2011-01-01 01:10"
            ), follow_redirects=True)  
    
    def make_bad_post_title(self):
        return self.app.post('/add', data=dict(
            title='',
            body='this should not work',
            post_on="2011-01-01 01:10"
            ), follow_redirects=True)
    
    def make_bad_post_body(self):
        return self.app.post('/add', data=dict(
            title='this should not work',
            body='',
            post_on="2011-01-01 01:10"
            ), follow_redirects=True)
    
    def make_bad_post_date(self):
        return self.app.post('/add', data=dict(
            title='this should not work',
            body='this should not work',
            post_on=""
            ), follow_redirects=True)
        
    def test_empty_db(self):
        rv = self.app.get('/')
        assert "No entries here so far" in rv.data
    
    def test_login_logout(self):
        rv = self.login(flaskr.app.config['ADMIN_USERNAME'], flaskr.app.config['ADMIN_PASSWORD'])
        assert "You were logged in" in rv.data
        rv = self.logout()
        assert "You were logged out" in rv.data
        rv = self.login('adminx', 'admin')
        assert "Invalid username" in rv.data
        rv = self.login('admin', 'adminx')
        assert "Invalid username" in rv.data
    
    def test_post_authenticated(self):
        rv = self.login(flaskr.app.config['ADMIN_USERNAME'], flaskr.app.config['ADMIN_PASSWORD'])
        assert "You were logged in" in rv.data
        rv = self.make_good_post()
        assert "this is a good post" in rv.data
    
    def test_post_unauthenticated(self):
        rv = self.logout()
        assert "You were logged out" in rv.data
        rv = self.make_good_post()
        assert "must be authenicated" in rv.data
        
    def test_post_bad_data(self):
        rv = self.login(flaskr.app.config['ADMIN_USERNAME'], flaskr.app.config['ADMIN_PASSWORD'])
        assert "You were logged in" in rv.data
        rv = self.make_good_post()
        assert "this is a good post" in rv.data
        rv = self.make_bad_post_title()
        assert "You must provide a title" in rv.data
        rv = self.make_bad_post_body()
        assert "Cat got your tongue?" in rv.data
        rv = self.make_bad_post_date()
        assert "Please input a date/time value" in rv.data
        
        

if __name__ == '__main__':
    unittest.main()