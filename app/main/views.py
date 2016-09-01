from flask import redirect, url_for, render_template
from flask.ext.login import current_user
from . import main


@main.route('/')
def index():
    return render_template("main/index.html")


@main.route('/statistics')
def statistics():
    return render_template("main/statistics.html")
