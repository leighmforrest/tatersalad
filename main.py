import os
import time

import jinja2
import webapp2
from google.appengine.ext import db

from models import Post, User, Comment
from security import (valid_username, valid_password, valid_email,
                      make_secure_val, check_secure_val, make_pwd_hash,
                      valid_pw)


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, key, val):
        cookie_val = make_secure_val(val)
        self.response.set_cookie(key, cookie_val)

    def check_secure_cookie(self, key):
        cookie_val = self.request.cookies.get(key)
        return cookie_val and check_secure_val(cookie_val)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.check_secure_cookie('uid')
        self.user = uid and User.get_user_by_id(uid)


class NewPostPage(Handler):

    def get(self):
        if not self.user:
            self.redirect('/')
        self.render('new_post.html')

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        author = self.user

        if subject and content:
            post = Post.create_post(subject, content, author)
            time.sleep(1)
            self.redirect('/{}'.format(post))

        else:
            error = "We need both a title and some content."
            self.render(
                'new_post.html', subject=subject, content=content, error=error)


class ShowPostPage(Handler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        # If not post, 404
        if not post:
            self.error(404)
        self.render('show_post.html', post=post, user=self.user)


class UpdatePostPage(Handler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        if not post and post.author == self.user:
            self.error(404)
        self.render('new_post.html',
                    post=post, subject=post.subject, content=post.content)

    def post(self, post_id):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            if Post.is_owner(self.user, post_id):
                post = Post.update_post(subject, content, post_id)
                time.sleep(1)
                self.redirect('/{}'.format(post))
            else:
                error = "Author an user are not the same."
                self.render('new_post.html',
                            subject=subject, content=content, error=error)

        else:
            error = "We need both a title and some content."
            self.render('new_post.html',
                        subject=subject, content=content, error=error)


class MainPage(Handler):
    def get(self):
        posts = Post.all().order('-created')
        self.render('index.html', posts=posts)


class SignupPage(Handler):
    def get(self):
        self.render("signup.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username=username,
                      email=email)

        if not valid_username(username):
            params['error_username'] = "That is not a valid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords did not match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if User.user_exists(username):
            params['error_username'] = "Username has been taken."
            have_error = True

        if have_error:
            self.render('signup.html', **params)
        else:
                # Make the hashed password.
                hashed_password = make_pwd_hash(username, password)
                # Set the user account in database
                uid = User.create_user(username, hashed_password)
                # set the cookie
                self.set_secure_cookie('uid', str(uid))
                # redirect
                self.redirect('/')


class AccountPage(Handler):
    def get(self):
        user = self.user
        self.render('welcome.html', user=user)


class LoginPage(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        params = dict(username=username)

        # check database
        user = User.gql("Where username = '%s'" % username).get()
        if user and valid_pw(username, password, user.password):
            uid = user.key().id()
            self.set_secure_cookie('uid', str(uid))
            self.redirect('/account')
        else:
            params['error_login'] = "The password and/or username do not match."
            have_error = True
            self.render('login.html', **params)


class LogoutHandler(Handler):
    """Handles login. Note: there is no temlate."""
    def get(self):
        self.response.delete_cookie('uid')
        self.redirect('/account/login')


class CommentHandler(Handler):
    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        author = self.user
        content = self.request.get("content")
        # If not post, 404
        if not post and author:
            self.error(404)
        else:
            Comment.create_comment(post_id, content, author)
            self.redirect(post.get_absolute_url())


app = webapp2.WSGIApplication(
    [('/', MainPage),
     ('/new_post', NewPostPage),
     ('/([0-9]+)', ShowPostPage),
     ('/([0-9]+)/comment', CommentHandler),
     ('/([0-9]+)/update', UpdatePostPage),
     ('/account/signup', SignupPage),
     ('/account', AccountPage),
     ('/account/login', LoginPage),
     ('/account/logout', LogoutHandler),
     ],
    debug=True)
