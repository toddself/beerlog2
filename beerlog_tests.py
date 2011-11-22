import os
import unittest
import tempfile
import hashlib
from datetime import datetime

from werkzeug.datastructures import FileStorage

import beerlog
from blog.models import get_slug_from_title, Entry, Users

class BeerlogTestCase(unittest.TestCase):
    
    post_date = "2011-01-01 11:45"
    
    def setUp(self):
        self.db_fd, beerlog.app.config['DB_NAME'] = tempfile.mkstemp()
        beerlog.app.config['TESTING'] = True
        self.app = beerlog.app.test_client()
        beerlog.connect_db(beerlog.app.config)
        beerlog.init_db(beerlog.app.config)
    
    def tearDown(self):
        os.unlink(beerlog.app.config['DB_NAME'])
        
    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
    
    def make_good_post(self, redirect=True):
        return self.app.post('/entry/edit/', data=dict(
            title='this is a good post',
            post="yessss",
            post_on=self.post_date
            ), follow_redirects=redirect)  
    
    def make_bad_post_title(self):
        return self.app.post('/entry/edit/', data=dict(
            title='',
            post='this should not work',
            post_on=self.post_date
            ), follow_redirects=True)
    
    def make_bad_post_body(self):
        return self.app.post('/entry/edit/', data=dict(
            title='this should not work',
            post='',
            post_on=self.post_date
            ), follow_redirects=True)
    
    def make_bad_post_date(self):
        return self.app.post('/entry/edit/', data=dict(
            title='this should not work',
            post='this should not work',
            post_on=""
            ), follow_redirects=True)
    
    def make_good_image_post(self):
        return self.app.post('/upload', data=dict(
            file=self.make_image_object(True)
        ))
    
    def make_bad_image_post(self):
        return self.app.post('/upload', data=dict(
            file=self.make_image_object(False)
        ))
        
    def make_image_object(self, good):
        if good:
            fn = 'test_image.png'
        else:
            fn = 'console.sh'
        
        fh = open(fn, "rb")
        return FileStorage(fh, fn)
        
    def good_login(self):
        rv = self.login(beerlog.app.config['ADMIN_USERNAME'], 
                        beerlog.app.config['ADMIN_PASSWORD'])
        assert "You were logged in" in rv.data

    def test_admin_created(self):
        username = beerlog.app.config['ADMIN_USERNAME']
        user = Users.select(Users.q.email==username)[0]
        assert user.email == beerlog.app.config['ADMIN_USERNAME']
        
    def test_empty_db(self):
        rv = self.app.get('/')
        assert "No entries matched your request" in rv.data
    
    def test_login_logout(self):
        self.good_login()
        rv = self.logout()
        assert "You were logged out" in rv.data
        rv = self.login('adminx', 'admin')
        assert "Invalid username" in rv.data
        rv = self.login('admin', 'adminx')
        assert "Invalid username" in rv.data
    
    def test_post_authenticated(self):
        self.good_login()
        rv = self.make_good_post()
        assert "this is a good post" in rv.data

    def test_slug_generation(self):
        self.good_login()
        rv = self.make_good_post()
        assert "this is a good post" in rv.data
        date = datetime.strptime(self.post_date, "%Y-%m-%d %H:%M")
        slug = get_slug_from_title("this is a good post")
        url = "/entry/%s/%s/%s/%s/" % (date.year, 
                                       date.month,
                                       date.day,
                                       slug)
        rv = self.app.get(url)
        assert "this is a good post" in rv.data
    
    def test_post_unauthenticated(self):
            rv = self.logout()
            assert "You were logged out" in rv.data
            rv = self.make_good_post()
            assert "must be authenticated" in rv.data
    
    def test_post_delete_authenticated(self):
        self.good_login()
        rv = self.make_good_post(redirect=False)
        post_id = rv.location.rsplit('/')[-2]
        rv = self.app.get('/entry/edit/%s/delete/' % post_id, 
                          follow_redirects=True)
        assert "marked as deleted" in rv.data
        
        
    def test_post_delete_unauthenticated(self):
        self.good_login()
        rv = self.make_good_post(redirect=False)
        post_id = rv.location.rsplit('/')[-2]
        rv = self.logout()
        assert "You were logged out" in rv.data
        rv = self.app.get('/entry/edit/%s/delete/' % post_id, 
                          follow_redirects=True)
        assert "must be authenticated" in rv.data
        
    # def test_post_no_title(self):
    #     rv = self.login(beerlog.app.config['ADMIN_USERNAME'], beerlog.app.config['ADMIN_PASSWORD'])
    #     assert "You were logged in" in rv.data
    #     rv = self.make_good_post()
    #     assert "this is a good post" in rv.data
    #     rv = self.make_bad_post_title()
    #     assert "You must provide a title" in rv.data
    # 
    # def test_post_no_body(self):
    #     rv = self.login(beerlog.app.config['ADMIN_USERNAME'], beerlog.app.config['ADMIN_PASSWORD'])
    #     assert "You were logged in" in rv.data
    #     rv = self.make_good_post()
    #     assert "this is a good post" in rv.data
    #     rv = self.make_bad_post_body()
    #     assert "Cat got your tongue?" in rv.data
    # 
    # def test_post_no_date(self):
    #     rv = self.login(beerlog.app.config['ADMIN_USERNAME'], beerlog.app.config['ADMIN_PASSWORD'])
    #     assert "You were logged in" in rv.data
    #     rv = self.make_good_post()
    #     assert "this is a good post" in rv.data
    #     rv = self.make_bad_post_date()
    #     assert "%Y-%m-%d %H:%M" in rv.data
    #     
    # def test_upload_image(self):
    #     rv = self.login(beerlog.app.config['ADMIN_USERNAME'], beerlog.app.config['ADMIN_PASSWORD'])
    #     assert "You were logged in" in rv.data
    #     rv = self.make_good_image_post()
    #     assert "Success" in rv.data
    #     rv = self.make_bad_image_post()
    #     assert "valid image" in rv.data

if __name__ == '__main__':
    unittest.main()