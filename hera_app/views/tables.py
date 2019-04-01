# import things
from flask_table import Table, Col
from flask import render_template, flash, redirect, url_for, jsonify, session, Blueprint
import json
from sqlalchemy import create_engine
import sqlalchemy as db
from hera_app import app


from flask_login import login_required
from hera_app.auth import User

# profile = Blueprint('profile', __name__,
#                     template_folder='templates',
#                     static_folder='static')
tables = Blueprint('tables', __name__)

engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

from .items import items, sample_states, sample_ids

# Declare your table
class ItemTable(Table):
    id = Col('id')
    username = Col('username')
    groups = Col('groups')
    classes = ['table', 'table-striped']
    allow_sort = True

    def sort_url(self, col_key, reverse=False):
        if reverse:
            direction = 'desc'
        else:
            direction = 'asc'
        return url_for('tables.index', sort=col_key, direction=direction)


@tables.route('/tables')
@login_required
def index():

    #  move to sth more persistent once columns are more finalized
    sample_id_db_columns = engine.execute(
        'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA="samplestatus"  AND TABLE_NAME="sample";'
    )
    sample_id_db_data = engine.execute('SELECT * FROM sample').fetchall()
    columnHeaders = generateColumnHeaders(sample_id_db_columns)
    data = generateData(sample_id_db_data, columnHeaders)
    return render_template('tables.html', columnHeaders=columnHeaders, data=data)


def generateColumnHeaders(dbColumns):
    sample_id_columns_dict = []
    sample_id_columns = []
    for row in dbColumns:
        sample_id_columns_dict = {"data": row[0], "title": row[0]}
        sample_id_columns.append(sample_id_columns_dict.copy())
    
    return sample_id_columns


def generateData(dbData, columnHeaders):
    sample_id_data_dict = {}
    sample_id_data = []
    for row in dbData:
        for i, col in enumerate(columnHeaders):
            sample_id_data_dict[col['data']] = '' if row[i] is None else row[i]
        sample_id_data.append(sample_id_data_dict.copy())
    return sample_id_data


@tables.route('/sample_timeline')
@login_required
def sample_timeline():
    return render_template('sample_timeline.html')


# sample timeline, get sample by id display state timeline
