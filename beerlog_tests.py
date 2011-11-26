import os
import unittest
import tempfile
import hashlib
from datetime import datetime
from random import choice as r_choice
from string import ascii_uppercase as au

from werkzeug.datastructures import FileStorage

import beerlog
from settings import DATE_FORMAT
from blog.models import get_slug_from_title, Entry, Users

class BeerlogTestCase(unittest.TestCase):

    post_date = "2011-01-01"
    post_time = "11:45"
    post_body = "This is a test of the posting function"
    post_title = "This is a !test!@post!!!"
    post_tags = "test, tags"

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

    def create_post(self, title, body, date, time, tags, redirect=True, pid=0):
        if pid:
            url = '/entry/edit/%s/' % pid
        else:
            url = '/entry/edit/'
        return self.app.post(url, data=dict(
            title=title,
            body=body,
            date=date,
            time=time,
            tags=tags
            ), follow_redirects=redirect)

    def create_image(self, filepath, follow=True):
        fh = open(fn, 'rb')
        return self.app.post('/upload', data=dict(
            file=FileStorage(fh, fn)
        ))

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
        rv = self.create_post(self.post_title,
                              self.post_body,
                              self.post_date,
                              self.post_time,
                              self.post_tags)
        assert self.post_title in rv.data

    def test_slug_generation(self):
        self.good_login()
        rv = self.create_post(self.post_title,
                              self.post_body,
                              self.post_date,
                              self.post_time,
                              self.post_tags)
        assert self.post_title in rv.data
        date = datetime.strptime(self.post_date, DATE_FORMAT)
        slug = get_slug_from_title(self.post_title)
        url = "/entry/%s/%s/%s/%s/" % (date.year,
                                       date.month,
                                       date.day,
                                       slug)
        rv = self.app.get(url)
        assert self.post_title in rv.data

    def test_post_unauthenticated(self):
            rv = self.logout()
            assert "You were logged out" in rv.data
            rv = self.create_post(self.post_title,
                                  self.post_body,
                                  self.post_date,
                                  self.post_time,
                                  self.post_tags)
            assert "must be authenticated" in rv.data

    def test_post_delete_authenticated(self):
        self.good_login()
        rv = self.create_post(self.post_title,
                              self.post_body,
                              self.post_date,
                              self.post_time,
                              self.post_tags,
                              redirect=False)
        print rv
        post_id = rv.location.rsplit('/')[-2]
        rv = self.app.get('/entry/edit/%s/delete/' % post_id,
                          follow_redirects=True)
        assert "marked as deleted" in rv.data

    def test_post_delete_unauthenticated(self):
        self.good_login()
        rv = self.create_post(self.post_title,
                              self.post_body,
                              self.post_date,
                              self.post_time,
                              self.post_tags,
                              False)
        post_id = rv.location.rsplit('/')[-2]
        rv = self.logout()
        assert "You were logged out" in rv.data
        rv = self.app.get('/entry/edit/%s/delete/' % post_id,
                          follow_redirects=True)
        assert "must be authenticated" in rv.data

    def test_multiple_posts_per_day(self):
        self.good_login()
        post_title2 = "post two"
        test_date = datetime.strptime(self.post_date, DATE_FORMAT)
        self.create_post(self.post_title,
                         self.post_body,
                         self.post_date,
                         self.post_time,
                         self.post_tags)
        self.create_post(post_title2,
                         self.post_body,
                         self.post_date,
                         self.post_time,
                         self.post_tags)
        rv = self.app.get('/entry/%s/%s/%s/' % (test_date.year,
                                                test_date.month,
                                                test_date.day))
        assert self.post_title in rv.data
        assert post_title2 in rv.data

    def test_bad_posts(self):
        self.good_login()
        # missing title
        rv = self.create_post("",
                              self.post_body,
                              self.post_date,
                              self.post_time,
                              self.post_tags)
        assert "You must provide a title" in rv.data
        # missing body
        rv = self.create_post(self.post_title,
                              "",
                              self.post_date,
                              self.post_time,
                              self.post_tags)
        assert "The body is required" in rv.data
        # too short body
        rv = self.create_post(self.post_title,
                              "ta",
                              self.post_date,
                              self.post_time,
                              self.post_tags)
        assert "The body is required" in rv.data
        # too long body
        rv = self.create_post(self.post_title,
                              ''.join(r_choice(au) for x in range(1048577)),
                              self.post_date,
                              self.post_time,
                              self.post_tags)
        assert "The body is required" in rv.data
        # malformed date
        rv = self.create_post(self.post_title,
                              self.post_body,
                              "AHAHAHHAHA",
                              self.post_time,
                              self.post_tags)
        assert "Invalid date/time input" in rv.data
        # malformed time
        rv = self.create_post(self.post_title,
                              self.post_body,
                              self.post_date,
                              "HAHAHAAHAH",
                              self.post_tags)
        assert "Invalid date/time input" in rv.data
    
    def test_post_edit(self):
        rv = self.create_post(self.post_title,
                              self.post_body,
                              self.post_date,
                              self.post_time,
                              self.post_tags,
                              False)
        post_id = rv.location.rsplit('/')[-2]
        rv = self.create_post("i am an edited post",
                              self.post_body,
                              self.post_date,
                              self.post_time,
                              self.post_tags,
                              True)
        assert "i am an edited post" in rv.data

if __name__ == '__main__':
    unittest.main()