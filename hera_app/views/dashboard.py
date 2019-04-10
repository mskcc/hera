import os
from flask import render_template, flash, redirect, url_for, jsonify, session, Blueprint
from flask_login import login_required
import time
import datetime
from datetime import datetime
from sqlalchemy import create_engine
import sqlalchemy as db
import json

import plotly

import pandas as pd
import numpy as np

import plotly.plotly as py
import plotly.figure_factory as ff
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot


from hera_app.auth import User
from hera_app import app

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])


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
    # return render_template("dashboard.html", samplesPerDay=samplesPerDay)
    graphs = [
        # dict(
        #     data=[dict(x=[1, 2, 3], y=[10, 20, 30], type='scatter')],
        #     layout=dict(title='first graph'),
        # ),
        # x = month/year y = #samples
        dict(
            data=[dict(x=samplesPerDay['x'], y=samplesPerDay['y'], type='bar')],
            layout=dict(title='second graph'),
        )
    ]
    # rng = pd.date_range('1/1/2011', periods=7500, freq='H')
    # ts = pd.Series(np.random.randn(len(rng)), index=rng)

    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('/dashboard.html', ids=ids, graphJSON=graphJSON)


# get all samples processed by day (includes Roslin noise states - maybe limit to group by sample id?)
def getSamplesPerDay():
    log_info("getting samplesPerDay")

    samplesPerDay_statement = (
        "SELECT count(*),  Year(date) FROM samplestatus.status GROUP BY YEAR(date);"
    )
    # samplesPerDay_statement = "SELECT count(*),  MONTH(date), Year(date) FROM samplestatus.status GROUP BY YEAR(date), MONTH(date);"

    samplesPerDay = engine.execute(samplesPerDay_statement)
    data = {'x':[],'y':[]}
    print(data['x'])
    for sample in samplesPerDay:
        data['x'].append(sample[1])
        data['y'].append(sample[0])
    return data


# @dashboard_blueprint.route('/dashboard')
# def dashboard():
#     rng = pd.date_range('1/1/2011', periods=7500, freq='H')
#     ts = pd.Series(np.random.randn(len(rng)), index=rng)

#     graphs = [
#         dict(
#             data=[dict(x=[1, 2, 3], y=[10, 20, 30], type='scatter')],
#             layout=dict(title='first graph'),
#         ),
#         dict(
#             data=[dict(x=[1, 3, 5], y=[10, 50, 30], type='bar')],
#             layout=dict(title='second graph'),
#         ),
#         dict(
#             data=[dict(x=ts.index, y=ts)]  # Can use the pandas data structures directly
#         ),
#         dict(
#             data=[
#                 dict(
#                     Task='Morning Sleep',
#                     Start='2016-01-01',
#                     Finish='2016-01-01 6:00:00',
#                     Resource='Sleep',type='gantt',
#                 ),
#                 dict(
#                     Task='Breakfast',
#                     Start='2016-01-01 7:00:00',
#                     Finish='2016-01-01 7:30:00',
#                     Resource='Food',type='gantt',
#                 ),
#                 dict(
#                     Task='Work',
#                     Start='2016-01-01 9:00:00',
#                     Finish='2016-01-01 11:25:00',
#                     Resource='Brain',type='gantt',
#                 ),
#                 dict(
#                     Task='Break',
#                     Start='2016-01-01 11:30:00',
#                     Finish='2016-01-01 12:00:00',
#                     Resource='Rest',type='gantt',
#                 ),
#                 dict(
#                     Task='Lunch',
#                     Start='2016-01-01 12:00:00',
#                     Finish='2016-01-01 13:00:00',
#                     Resource='Food',type='gantt',
#                 ),
#                 dict(
#                     Task='Work',
#                     Start='2016-01-01 13:00:00',
#                     Finish='2016-01-01 17:00:00',
#                     Resource='Brain',type='gantt',
#                 ),
#                 dict(
#                     Task='Exercise',
#                     Start='2016-01-01 17:30:00',
#                     Finish='2016-01-01 18:30:00',
#                     Resource='Cardio',type='gantt',
#                 ),
#                 dict(
#                     Task='Post Workout Rest',
#                     Start='2016-01-01 18:30:00',
#                     Finish='2016-01-01 19:00:00',
#                     Resource='Rest',type='gantt',
#                 ),
#                 dict(
#                     Task='Dinner',
#                     Start='2016-01-01 19:00:00',
#                     Finish='2016-01-01 20:00:00',
#                     Resource='Food',type='gantt',
#                 ),
#                 dict(
#                     Task='Evening Sleep',
#                     Start='2016-01-01 21:00:00',
#                     Finish='2016-01-01 23:59:00',
#                     Resource='Sleep',type='gantt',

#                 ),
#             ]
#         ),
#     ]

#     # Add "ids" to each of the graphs to pass up to the client
#     # for templating
#     ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

#     fig = ff.create_gantt(
#         df,
#         colors=colors,
#         index_col='Resource',
#         title='Daily Schedule',
#         show_colorbar=True,
#         bar_width=0.8,
#         showgrid_x=True,
#         showgrid_y=True,
#     )
#     # iplot(fig)

#     # Convert the figures to JSON
#     # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
#     # objects to their JSON equivalents
#     graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
#     return render_template('/dashboard.html', ids=ids, graphJSON=graphJSON)
