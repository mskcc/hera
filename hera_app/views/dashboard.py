import os
from flask import render_template, flash, redirect, url_for, jsonify, session, Blueprint
from flask_login import login_required
import time
import datetime
from datetime import datetime

import mysql.connector
import json


from hera_app.auth import User
from hera_app import app


db = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    port=app.config['MYSQL_PORT'],
    user=app.config['MYSQL_USER'],
    passwd=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB'],
)

dbcursor = db.cursor()

dashboard_blueprint = Blueprint("dashboard", __name__)


def log_error(*args):
    print("HERA_ERROR:"),
    for arg in args:
        print(arg),
    print()


def log_info(*args):
    print("HERA_INFO:"),
    for arg in args:
        print(arg),
    print()


@dashboard_blueprint.route("/dashboard")
@login_required
def dashboard():
    samplesPerDay = getSamplesPerDay()
    return render_template("dashboard.html", samplesPerDay=samplesPerDay)


# get all samples processed by day (includes Roslin noise states - maybe limit to group by sample id?)
def getSamplesPerDay():
    log_info("getting samplesPerDay")

    samplesPerDay_statement = "SELECT count(*),  MONTH(date), Year(date) FROM samplestatus.status GROUP BY YEAR(date), MONTH(date);"

    # get altIds for project samples
    dbcursor.execute(samplesPerDay_statement)

    samplesPerDay = dbcursor.fetchall()
    for sample in samplesPerDay:
        print(sample)
