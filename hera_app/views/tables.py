# import things
from flask_table import Table, Col
from flask import render_template, flash, redirect, url_for, jsonify, session, Blueprint
import json

from flask_login import login_required
from hera_app.auth import User

# profile = Blueprint('profile', __name__,
#                     template_folder='templates',
#                     static_folder='static')
tables = Blueprint('tables', __name__)

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
    # items = User.query.all() + User.query.all() + User.query.all()
    # table = ItemTable(items)
    # print(jsonify(json_list = items))
    # print(jsonify([i.serialize for i in items]).data)
    # print(tables)
    # return render_template('tables.html', table=table)
    print(sample_ids)
    return render_template(
        'tables.html',
        items=items,
        samples=items,
        sample_states=sample_states,
        sample_ids=sample_ids,
    )


@tables.route('/sample_timeline')
@login_required
def sample_timeline():
    return render_template('sample_timeline.html')


# sample timeline, get sample by id display state timeline
