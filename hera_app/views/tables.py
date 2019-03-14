# import things
from flask_table import Table, Col
from flask import render_template, flash, redirect, url_for, jsonify, session, Blueprint
import json
from sqlalchemy import create_engine
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
    sample_id_db_columns = engine.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA="samplestatus"  AND TABLE_NAME="sample";')
    sample_id_db_data = engine.execute('SELECT * FROM sample')

    sample_id_columns_dict = {}
    sample_id_columns = []
    for row in sample_id_db_columns:
        sample_id_columns_dict['name'] = row[0]
        sample_id_columns_dict['type'] = 'text'
        sample_id_columns_dict['align'] = 'left'
        sample_id_columns.append(sample_id_columns_dict.copy())

    # sample_columns = engine.execute('SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA="samplestatus"  AND TABLE_NAME="sample";')


    sample_id_data_dict = {}
    sample_id_data = []
    for row in sample_id_db_data:
        sample_id_data_dict['id'] = row[0]
        sample_id_data_dict['altId'] = row[1]
        sample_id_data_dict['correctedCmoId'] = row[2]
        sample_id_data_dict['investigatorEmail'] = row[3]
        sample_id_data_dict['userSampleId'] = row[4]
        sample_id_data.append(sample_id_data_dict.copy())


    print(sample_id_columns)


    # sample_result = engine.execute('SELECT * FROM sample')
    # print(sample_result)
    # items = User.query.all() + User.query.all() + User.query.all()
    # table = ItemTable(items)
    # print(jsonify(json_list = items))
    # print(jsonify([i.serialize for i in items]).sample_id_columns)
    # print(tables)
    # return render_template('tables.html', table=table)
    # print(sample_ids)
    return render_template(
        'tables.html',
        items=items,
        samples=items,
        sample_states=sample_states,
        sample_id_data=sample_id_data,
        sample_id_columns = sample_id_columns
    )


@tables.route('/sample_timeline')
@login_required
def sample_timeline():
    return render_template('sample_timeline.html')


# sample timeline, get sample by id display state timeline
