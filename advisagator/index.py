""" undocumented """

import flask

from advisagator import app


@app.route("/")
def index():
    """ Render the default page """
    return flask.render_template("index.html")


@app.route("/logout/")
def logout():
    """ Execute the logout endpoint """
    flask.session.pop("id", None)
    flask.session.pop("isTeacher", None)
    return flask.redirect("/")
