from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

social_db = SQLAlchemy()
bcrypt = Bcrypt()


def social_connect_db(app):
    """Connect to database."""

    social_db.app = app
    social_db.init_app(app)


class Follows(social_db.Model):
    """Connection of a follower <-> followed_user."""

    __tablename__ = 'follows'

    user_being_followed_id = social_db.Column(
        social_db.Integer,
        social_db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = social_db.Column(
        social_db.Integer,
        social_db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

class User(social_db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = social_db.Column(
        social_db.Integer,
        primary_key=True,
    )

    username = social_db.Column(
        social_db.Text,
        nullable=False,
        unique=True
    )

    password = social_db.Column(
        social_db.Text,
        nullable=False
    )

    followers = social_db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    following = social_db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )


    posts = social_db.relationship('Post', backref='users')



    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1
    

    @classmethod
    def signup(cls, username, password):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
        )

        social_db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    
    @classmethod
    def username_authenticate(cls, username):
        """Make sure username is not taken"""

        user = cls.query.filter_by(username=username).first()

        if not user:
            return True
        else:
            return False

class Post(social_db.Model):
    """An individual post."""

    __tablename__ = 'posts'

    id = social_db.Column(
        social_db.Integer,
        primary_key=True,
    )

    title = social_db.Column(
        social_db.Text,
        nullable=False,
    )

    body = social_db.Column(
        social_db.Text,
        nullable=False,
    )

    user_id = social_db.Column(
        social_db.Integer,
        social_db.ForeignKey('users.id', ondelete='CASCADE'),
        
    )

    

class Likes(social_db.Model):
    """Mapping user likes to posts."""

    __tablename__ = 'likes' 

    id = social_db.Column(
        social_db.Integer,
        primary_key=True
    )

    user_id = social_db.Column(
        social_db.Integer,
        social_db.ForeignKey('users.id', ondelete='cascade')
    )

    post_id = social_db.Column(
        social_db.Integer,
        social_db.ForeignKey('posts.id', ondelete='cascade'),
        unique=True
    ) 





