"""This module adds methods related to the security of the application."""
import re
import random
import hmac
import hashlib
import string


# WARNING: for a real, non-roody-poo app, put this in environment variable.
APP_SECRET = 'hNGHMxtFKVdOvLWiSTWpJdKGZ'
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


def valid_username(username):
    """Checks for a valid username. Uses a regular expression."""
    return username and USER_RE.match(username)


def valid_password(password):
    """Checks for a valid password. Uses a regular expression."""
    return password and PASS_RE.match(password)


def valid_email(email):
    """Checks for a valid email address."""
    return not email or EMAIL_RE.match(email)


def hash_str(unsafe_string):
    """Hash an unsafe string using HMAC"""
    return hmac.new(APP_SECRET, unsafe_string).hexdigest()


def make_secure_val(unsafe_string):
    """Make a secure string."""
    return "{0}|{1}".format(unsafe_string, hash_str(unsafe_string))


def check_secure_val(safe_string):
    """Validate a secure string."""
    val = safe_string.split('|')[0]
    if safe_string == make_secure_val(val):
        return val


def make_salt():
    """Generates a five-character random string for hashing."""
    return ''.join(random.choice(string.letters) for _ in range(5))


def make_pwd_hash(name, pwd, salt=None):
    """Hash a password using SHA256."""
    if not salt:
        salt = make_salt()

    hashe = hashlib.sha256(name + pwd + salt).hexdigest()
    return "{0},{1}".format(hashe, salt)


def valid_pw(name, pwd, hashe):
    """Make sure the password is correct."""
    salt = hashe.split(',')[1]
    return hashe == make_pwd_hash(name, pwd, salt)
