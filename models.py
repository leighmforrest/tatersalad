from google.appengine.ext import db


class DateTimeModel(db.Model):
    """Instantiates with created and updated times. All models in the app will
    descend from DateTimeModel."""
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)


class User(DateTimeModel):
    """Models a user."""
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)

    @classmethod
    def create_user(cls, username, hashed_password):
        """Method to add a user. Passwords are assumed to be hashed."""
        user = User(username=username, password=hashed_password)
        user.put()

        return user.key().id()

    @classmethod
    def get_user_by_id(cls, uid):
        """Get a user by his/her id."""
        return User.get_by_id(int(uid))

    @classmethod
    def user_exists(cls, username):
        """Returns true if user exists in the system."""
        user = User.gql("WHERE username = '%s'" % username).get()
        if user:
            return True
        else:
            return False


class Post(DateTimeModel):
    """Class that contains the data needed for a blog post."""
    #  blog = db.ReferenceProperty(Blog, collection_name='posts')
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    author = db.ReferenceProperty(User,
                                  required=True,
                                  collection_name='posts')

    def get_absolute_url(self):
        """Get the url to show a post."""
        return '/{}'.format(self.key().id())

    def html_text(self):
        """Returns the string replacing newlines with a break tag."""
        return self.content.replace('\n', '<br>')

    @classmethod
    def create_post(cls, subject, content, author):
        """Method to add a post."""
        post = Post(subject=subject, content=content, author=author)
        post.put()
        return post.key().id()

    @classmethod
    def update_post(cls, subject, content, post_id):
        post = Post.get_by_id(int(post_id))
        if post:
            post.subject = subject
            post.content = content
            post.put()
            return post.key().id()

    @classmethod
    def is_owner(cls, user, post_id):
        post = Post.get_by_id(int(post_id))
        return user.key().id() == post.author.key().id()

    @classmethod
    def delete_post(cls, post_id):
        post = Post.get_by_id(int(post_id))
        if post:
            post.delete()
            return True
        else:
            return False


class Comment(DateTimeModel):
    content = db.TextProperty(required=True)
    post = db.ReferenceProperty(Post, required=True,
                                collection_name='comments')
    author = db.ReferenceProperty(User,
                                  required=True,
                                  collection_name='author_comments')

    @classmethod
    def create_comment(cls, post_id, content, author):
        """Method to add a post."""
        post = Post.get_by_id(int(post_id))
        comment = Comment(post=post, content=content, author=author)
        comment.put()
        return comment.key().id()

    @classmethod
    def update_comment(cls, comment_id, content):
        comment = Comment.get_by_id(int(comment_id))
        if comment:
            comment.content = content
            comment.put()
            return comment.key().id()

    @classmethod
    def delete_comment(cls, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        if comment:
            comment.delete()
            return True
        else:
            return False


class Like(DateTimeModel):
    """Models a like. Holds references to user and post."""
    user = db.ReferenceProperty(User,
                                required=True,
                                collection_name='likes')
    post = db.ReferenceProperty(Post,
                                required=True,
                                collection_name='likes')

    @classmethod
    def by_post_id(cls, post_id):
        """Get number of likes for a post id"""
        likes = Like.all().filter('post =', post_id)
        return likes.count()
