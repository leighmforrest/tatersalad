import os
import time

import jinja2
import webapp2
from google.appengine.ext import db

from models import Post, User, Comment, Like
from security import (valid_username, valid_password, valid_email,
                      make_secure_val, check_secure_val, make_pwd_hash,
                      valid_pw)

# Templates
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    """Generic handler. All Handlers inherit from handler."""
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        """Render a template and data to be sent to template."""
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, key, val):
        """Sets a cookie. All cookies are secured."""
        cookie_val = make_secure_val(val)
        self.response.set_cookie(key, cookie_val)

    def check_secure_cookie(self, key):
        """Checks a cookie against a hash."""
        cookie_val = self.request.cookies.get(key)
        return cookie_val and check_secure_val(cookie_val)

    def initialize(self, *a, **kw):
        """"""
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.check_secure_cookie('uid')
        self.user = uid and User.get_user_by_id(uid)


class NewPostPage(Handler):
    """Handles the get and set methods of posting a post."""
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
            self.redirect('/{}'.format(post))

        else:
            error = "We need both a title and some content."
            self.render(
                'new_post.html', subject=subject, content=content, error=error)


class ShowPostPage(Handler):
    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        comments = post.comments.order('-created')
        # If not post, 404
        if not post:
            return self.error(404)
        # TODO: If user already liked post, set liked to True
        self.render('show_post.html',
                    post=post,
                    user=self.user,
                    )


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
        """Shows the ten most recent posts."""
        posts = Post.all().order('-created')[:10]
        self.render('index.html', posts=posts)


class SignupPage(Handler):
    def get(self):
        """Display the signup form."""
        self.render("signup.html")

    def post(self):
        """Validates the user's data and saves it."""
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
                self.redirect('/account')


class AccountPage(Handler):
    """Welcomes a logged in or new member. Page also displays posts created."""
    def get(self):
        user = self.user
        self.render('welcome.html', user=user)


class LoginPage(Handler):
    """Handles the get and post methods of the login page."""
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
        self.redirect('/')


class CommentHandler(Handler):
    """Handles a comment. Note there is no get method."""
    def post(self, post_id):
        """Posts a comment to a post."""
        post = Post.get_by_id(int(post_id))
        author = self.user
        content = self.request.get("content")
        # If not post, 404
        if not post and author:
            self.error(404)
        # If there is no  content, just redirect.
        # Would like to render the post's detail page with error message.
        elif not content:
            self.redirect(post.get_absolute_url())
        else:
            # Create a comment and redirect to the post's page.
            Comment.create_comment(post_id, content, author)
            # time.sleep(1)
            self.redirect(post.get_absolute_url())


class UpdateCommentPage(Handler):
    def get(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        post = comment.post

        if not self.user.key().id() == comment.author.key().id():
            self.error(404)
        else:
            self.render('edit_comment_post.html', comment=comment, post=post)

    def post(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        content = self.request.get("content")

        if not comment and comment.author.key().id() == self.user.key().id():
            self.error(404)
        elif not content:
            # If post does not have content, render the page with an error.
            error = "Comment must have content."
            post = comment.post
            self.render('edit_comment_post.html',
                        comment=comment, post=post, error=error)
        else:
            Comment.update_comment(comment_id, content)
            time.sleep(1)
            self.redirect(comment.post.get_absolute_url())


class DeleteCommentHandler(Handler):
    """Handles a comment delete. Notice there is no get method."""
    def post(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        post = comment.post
        if comment and comment.author.key().id() == self.user.key().id():
            if Comment.delete_comment(comment_id):
                # time.sleep(1) comment time.sleep in production
                self.redirect('/{}'.format(post.key().id()))
        else:
            self.error(404)


class DeletePostHandler(Handler):
    """Handle a post delete. Notice there is no get method."""
    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        if not post:
            print "Post does not exist"
            return self.error(404)
        # post.author != self.user would not work
        elif post and post.author.key().id() != self.user.key().id():
            print("{0} is not {1}".format(post.author, self.user))
            print "You don't own the post"
            return self.error(404)
        elif post and post.author.key().id() == self.user.key().id():
            post.delete()
            time.sleep(1)
            self.redirect('/account')
        else:
            # Thrw error if there is something unusual.
            self.error(404)


class LikeHandler(Handler):
    """Posts a like to a post. Note there is only a post method."""
    def post(self, post_id):
        post = Post.get_by_id(int(post_id))
        if post and post.author.key().id() == self.user.key().id():
            self.error(404)
        else:
            like = Like(post=post, user=self.user)
            like.put()
            time.sleep(1)
            self.redirect('/{}'.format(post_id))

"""All of the urls in the application."""
app = webapp2.WSGIApplication(
    [('/', MainPage),
     ('/new_post', NewPostPage),
     ('/([0-9]+)', ShowPostPage),
     ('/([0-9]+)/comment', CommentHandler),
     ('/([0-9]+)/like', LikeHandler),
     ('/([0-9]+)/update', UpdatePostPage),
     ('/account/signup', SignupPage),
     ('/account', AccountPage),
     ('/account/login', LoginPage),
     ('/account/logout', LogoutHandler),
     ('/([0-9]+)/delete', DeletePostHandler),
     ('/comment/([0-9]+)/update', UpdateCommentPage),
     ('/comment/([0-9]+)/delete', DeleteCommentHandler),
     ],
    debug=True)
