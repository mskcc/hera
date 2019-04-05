# import things
from flask import render_template, flash, redirect, url_for, jsonify, session, Blueprint
import json
from sqlalchemy import create_engine
import sqlalchemy as db
from hera_app import app
from datetime import datetime

from flask_login import login_required
from hera_app.auth import User

# profile = Blueprint('profile', __name__,
#                     template_folder='templates',
#                     static_folder='static')
tables = Blueprint("tables", __name__)

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])


@tables.route("/samples")
@login_required
def samples():
    #  move to sth more persistent once columns are more finalized
    sample_id_db_columns = engine.execute(
        'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA="samplestatus"  AND TABLE_NAME="sample";'
    )
    sample_id_db_data = engine.execute("SELECT * FROM sample").fetchall()
    columnHeaders = generateColumnHeaders(sample_id_db_columns)
    data = generateSampleData(sample_id_db_data, columnHeaders)
    return render_template("samples.html", columnHeaders=columnHeaders, data=data)


@tables.route("/status")
@tables.route("/status/<sample_id>")
@login_required
def status(sample_id=None):
    #  move to sth more persistent once columns are more finalized
    status_db_columns = engine.execute(
        'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA="samplestatus"  AND TABLE_NAME="status";'
    )
    # TODO grab from state table eventually
    distict_states = engine.execute("SELECT DISTINCT state FROM status").fetchall()
    states = [r for r, in distict_states]
    columnHeaders = [{'data': 'fk_sample_id', 'title': 'sample_id'}, {'data': 'state', 'title': 'state'},  {'data': 'date', 'title': 'date'}, {'data': 'id', 'title': 'id'}]
    # print(columnHeaders)
    # columnHeaders = generateColumnHeaders(status_db_columns)

    if sample_id is None:
        status_db_data = engine.execute("SELECT fk_sample_id, state, date, id FROM status").fetchall()
        data = generateStatusData(status_db_data, columnHeaders)
        return render_template(
            "status.html", columnHeaders=columnHeaders, data=data, states=states
        )
    else:
        status_db_data = engine.execute(
            "SELECT fk_sample_id, state, date, id FROM status WHERE fk_sample_id=" + sample_id
        ).fetchall()
        data = generateStatusData(status_db_data, columnHeaders)
        vis_data = generateVisData(status_db_data)
        return render_template(
            "single_status.html", columnHeaders=columnHeaders, data=data, vis_data=vis_data,sample_id=sample_id
        )
    
    


def generateColumnHeaders(dbColumns):
    columns_dict = []
    columns = []
    for row in dbColumns:
        columns_dict = {"data": row[0], "title": row[0]}
        columns.append(columns_dict.copy())

    return columns



def generateStatusData(dbData, columnHeaders):
    data_dict = {}
    data = []
    for row in dbData:
        for i, col in enumerate(columnHeaders):
            data_dict[col["data"]] = "" if row[i] is None else str(row[i])
        data.append(data_dict.copy())
    return data


def generateVisData(dbData):
    data_dict = {}
    data = []
    for i, row in enumerate(dbData):
        data_dict = {"id": row['id'], "content": row['state'], "start":row['date'].strftime("%Y-%m-%d")}
        data.append(data_dict.copy())
    print(data)
    return data


def generateSampleData(dbData, columnHeaders):
    data_dict = {}
    data = []
    for row in dbData:
        for i, col in enumerate(columnHeaders):

            data_dict[col["data"]] = "" if row[i] is None else str(row[i])
            # make id's clickable
            if col["data"] == 'id':
                data_dict[col["data"]] = (
                    '<a href="/status/' + str(row[i]) + '">' + str(row[i]) + '</a>'
                )

        data.append(data_dict.copy())
    return data


@tables.route("/sample_timeline")
@login_required
def sample_timeline():
    return render_template("sample_timeline.html")


# sample timeline, get sample by id display state timeline
