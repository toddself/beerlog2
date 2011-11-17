import os
import beerlog
import unittest
import tempfile
import hashlib

class BeerlogTestCase(unittest.TestCase):
    
    def setUp(self):
        self.db_fd, beerlog.app.config['DB_NAME'] = tempfile.mkstemp()
        beerlog.app.config['TESTING'] = True
        self.app = beerlog.app.test_client()
        beerlog.init_db()
    
    def tearDown(self):
        os.unlink(beerlog.app.config['DB_NAME'])
        
    def test_admin_created(self):
        user = beerlog.Users.select(beerlog.Users.q.email==beerlog.app.config['ADMIN_USERNAME'])[0]
        assert user.email == beerlog.app.config['ADMIN_USERNAME']

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
            post="yessss",
            post_on="2011-01-01 01:10"
            ), follow_redirects=True)  
    
    def make_bad_post_title(self):
        return self.app.post('/add', data=dict(
            title='',
            post='this should not work',
            post_on="2011-01-01 01:10"
            ), follow_redirects=True)
    
    def make_bad_post_body(self):
        return self.app.post('/add', data=dict(
            title='this should not work',
            post='',
            post_on="2011-01-01 01:10"
            ), follow_redirects=True)
    
    def make_bad_post_date(self):
        return self.app.post('/add', data=dict(
            title='this should not work',
            post='this should not work',
            post_on=""
            ), follow_redirects=True)
    
    def make_image_post(self):
        return self.app.post
        
    def test_empty_db(self):
        rv = self.app.get('/')
        assert "No entries here so far" in rv.data
    
    def test_login_logout(self):
        rv = self.login(beerlog.app.config['ADMIN_USERNAME'], beerlog.app.config['ADMIN_PASSWORD'])
        assert "You were logged in" in rv.data
        rv = self.logout()
        assert "You were logged out" in rv.data
        rv = self.login('adminx', 'admin')
        assert "Invalid username" in rv.data
        rv = self.login('admin', 'adminx')
        assert "Invalid username" in rv.data
    
    def test_post_authenticated(self):
        rv = self.login(beerlog.app.config['ADMIN_USERNAME'], beerlog.app.config['ADMIN_PASSWORD'])
        assert "You were logged in" in rv.data
        rv = self.make_good_post()
        assert "this is a good post" in rv.data
    
    def test_post_unauthenticated(self):
        rv = self.logout()
        assert "You were logged out" in rv.data
        rv = self.make_good_post()
        assert "must be authenicated" in rv.data
        
    def test_post_no_title(self):
        rv = self.login(beerlog.app.config['ADMIN_USERNAME'], beerlog.app.config['ADMIN_PASSWORD'])
        assert "You were logged in" in rv.data
        rv = self.make_good_post()
        assert "this is a good post" in rv.data
        rv = self.make_bad_post_title()
        assert "You must provide a title" in rv.data

    def test_post_no_body(self):
        rv = self.login(beerlog.app.config['ADMIN_USERNAME'], beerlog.app.config['ADMIN_PASSWORD'])
        assert "You were logged in" in rv.data
        rv = self.make_good_post()
        assert "this is a good post" in rv.data
        rv = self.make_bad_post_body()
        assert "Cat got your tongue?" in rv.data

    def test_post_no_date(self):
        rv = self.login(beerlog.app.config['ADMIN_USERNAME'], beerlog.app.config['ADMIN_PASSWORD'])
        assert "You were logged in" in rv.data
        rv = self.make_good_post()
        assert "this is a good post" in rv.data
        rv = self.make_bad_post_date()
        assert "%Y-%m-%d %H:%M" in rv.data
        
    def test_upload_image(self):
        rv = self.login(beerlog.app.config['ADMIN_USERNAME'], beerlog.app.config['ADMIN_PASSWORD'])
        assert "You were logged in" in rv.data
        rv = self.make_image_post()
        assert hashlib.md5('test_image.png') in rv.data
        
        
        

if __name__ == '__main__':
    unittest.main()