import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app, app
)
from werkzeug.security import check_password_hash, generate_password_hash
import json
from flaskr import firebase
from flaskr import FBauth

# from flaskr import db.session
bp = Blueprint('auth', __name__, url_prefix='/auth')


# This creates a Blueprint named 'auth'. Like the application object,
# the blueprint needs to know where it’s defined, so __name__ is passed
# as the second argument. The url_prefix will be prepended to all the URLs
# associated with the blueprint.
#
# Import and register the blueprint from the factory using app.register_blueprint().
# Place the new code at the end of the factory function before returning the app.

# You’ve written the authentication views for your application, but if you’re running
# the server and try to go to any of the URLs, you’ll see a TemplateNotFound error.
# That’s because the views are calling render_template(), but you haven’t written the
# templates yet. The template files will be stored in the templates directory inside
# the flaskr package.
#
# Templates are files that contain static data as well as placeholders for dynamic data.
# A template is rendered with specific data to produce a final document. Flask uses the
# Jinja template library to render templates.
#
# In your application, you will use templates to render HTML which will display in the
# user’s browser. In Flask, Jinja is configured to autoescape any data that is rendered
# in HTML templates. This means that it’s safe to render user input; any characters
# they’ve entered that could mess with the HTML, such as < and > will be escaped with
# safe values that look the same in the browser but don’t cause unwanted effects.
#
# Jinja looks and behaves mostly like Python. Special delimiters are used to distinguish
# Jinja syntax from the static data in the template. Anything between {{ and }} is an
# expression that will be output to the final document. {% and %} denotes a control flow
# statement like if and for. Unlike Python, blocks are denoted by start and end tags rather
# than indentation since static text within a block could change indentation.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                temp = FBauth.create_user_with_email_and_password(username, password)
            except Exception as error1:
                err = json.loads(str(error1).split(']', 1)[1])[
                    'error']  # occur if the username already exists occur if the username already exists
                error = err['message']  # occur if the username already exists occur if the username already exists
            #     error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
        #     url_for('hello', who='World')

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        user = None
        try:
            user = FBauth.sign_in_with_email_and_password(username, password)
        except:
            error = 'Incorrect username or password.'
        if error is None:
            session.clear()
            session['user_id'] = user['localId']
            session['email'] = user['email']
            g.user = {
                'email': user['email'],
                'user_id': user['localId'],
            }
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
        session.clear()
    else:
        g.user = {'email': session.get('email'),
              'user_id': session.get('user_id')}


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
