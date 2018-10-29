from flask import Flask, g, request, redirect, current_app, Response
from maintain_frontend.dependencies.session_api.session import Session
from maintain_frontend.constants.permissions import Permissions
from werkzeug.contrib.fixers import ProxyFix
import uuid
import requests
import datetime

app = Flask(__name__, static_url_path='/static/maintain-frontend')

app.config.from_pyfile("config.py")
app.wsgi_app = ProxyFix(app.wsgi_app)


@app.before_request
def before_request():
    """Request handler which will be called before the request is passed to any routes."""
    # If request is for static content then skip
    if '/static/' in request.path:
        return
    # Sets the transaction trace id into the global object if it has been provided in the HTTP header from the caller.
    # Generate a new one if it has not. We will use this in log messages.
    g.trace_id = request.headers.get('X-Trace-ID', uuid.uuid4().hex)
    g.application_permissions = Permissions
    # We also create a session-level requests object for the app to use with the header pre-set, so other APIs will
    # receive it. These lines can be removed if the app will not make requests to other LR APIs!
    g.requests = requests.Session()
    g.requests.headers.update({'X-Trace-ID': g.trace_id})

    if '/health' in request.path:
        return

    session_key = None
    if Session.session_cookie_name in request.cookies:
        session_key = request.cookies[Session.session_cookie_name]

    if session_key is None:
        return build_no_session_response('/sign-in')

    sess = Session(session_key)

    if not sess.valid():
        # Redirect to logout to clear session as invalid
        return build_no_session_response('/logout')

    # Shouldn't be possible to not have the JWT, but redirect to /login instead of
    # 'Something went wrong' if the JWT is missing
    if sess.user is not None and sess.user.jwt is not None:
        jwt = sess.user.jwt
    else:
        return build_no_session_response('/sign-in')

    g.session = sess
    g.requests.headers.update({'Authorization': 'Bearer ' + jwt})


def build_no_session_response(path):
    expire_date = datetime.datetime.now()
    expire_date = expire_date + datetime.timedelta(minutes=5)
    redirect_to_logout = redirect(path)

    if not request.is_xhr:
        response = current_app.make_response(redirect_to_logout)
        response.set_cookie('Location', value=request.path, httponly=True, expires=expire_date)
        return response

    return Response("{}", status=403, mimetype='application/json')
