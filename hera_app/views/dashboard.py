import os
from flask import render_template, flash, redirect, url_for, jsonify, session, Blueprint
from flask_login import login_required
import time
import datetime
from datetime import datetime
import calendar
from sqlalchemy import create_engine
import sqlalchemy as db
import json

import plotly

import pandas as pd
import numpy as np

import plotly.plotly as py
import plotly.figure_factory as ff
from plotly import tools
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
@dashboard_blueprint.route("/")
@login_required
def dashboard():
    igoSamplesYear = getIGOSamplesYear()
    # samplesProcessedInRoslinDaily = getSamplesProcessedInRoslinDaily()
    igoSamplesPast3 = getIGOSamplesPast3()
    roslinSamplesPast3 = getRoslinSamplesPast3()
    roslinSamplesByYear = getRoslinSamplesByYear()
    piSamples = getPiSamples()
    tumorTypes = getTumorTypes()
    # return render_template("dashboard.html", igoSamplesYear=igoSamplesYear)
    graphs = [
        # dict(
        #     data=[dict(x=[1, 2, 3], y=[10, 20, 30], type='scatter')],
        #     layout=dict(title='first graph'),
        # ),
        # x = month/year y = #samples
        dict(
            data=[
                dict(
                    x=igoSamplesYear['x'],
                    y=igoSamplesYear['y'],
                    type='bar',
                    marker=dict(color='#83276B'),
                )
            ],
            layout=dict(
                title='IGO Samples Received Per Year',
                autosize=False,
                width=500,
                height=500,
            ),
        ),
        dict(
            data=[
                dict(
                    x=roslinSamplesByYear['x'],
                    y=roslinSamplesByYear['y'],
                    width="0.4",
                    type='bar',
                    marker=dict(color='#DF4602'),

            )],
            layout=dict(
                title='Roslin Samples Received By Year',
                autosize=False,
                width=500,
                height=500,
                xaxis=dict(
                        nticks = len(roslinSamplesByYear['x'])+1
                        )
                )
            
        ),
        dict(
            data=[
                dict(
                    x=igoSamplesPast3['x'],
                    y=igoSamplesPast3['y'],
                    type='bar',
                    marker=dict(color='#40B4E5'),

                )
            ],
            layout=dict(
                title='IGO Samples Received last 3 months',
                autosize=False,
                width=500,
                height=500,
            ),
        ),
        dict(
            data=[
                dict(
                    x=roslinSamplesPast3['x'],
                    y=roslinSamplesPast3['y'],
                    type='bar',
                    marker=dict(color='#4C8B2B'),
                )
            ],
            layout=dict(
                title='Roslin Samples Received last 3 months',
                autosize=False,
                width=500,
                height=500,
            ),
        ),
        dict(
            data=[
                dict(
                    labels=piSamples['labels'],
                    values=piSamples['values'],
                    type='pie',
                    marker=dict(color='#83276B'),
                )
            ],
            layout=dict(
                title='Top Ten PIs by Number of WES Samples',
                autosize=False,
                width=500,
                height=500,
            ),
        ),
        dict(
            data=[
                dict(
                    labels=tumorTypes['y'],
                    values=tumorTypes['x'],
                    type='pie',
                    marker=dict(color='#83276B'),
                )
            ],
            layout=dict(title='Tumor Types', autosize=False, width=500, height=500),
        ),
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
def getIGOSamplesYear():

    igoSamplesYear_statement = "SELECT count(*),  Year(date) FROM samplestatus.status WHERE state = 'IGO_RECEIVED' GROUP BY YEAR(date);"
    log_info('IGO samples by year',igoSamplesYear_statement)
    igoSamplesYear = engine.execute(igoSamplesYear_statement)
    data = {'x': [], 'y': []}
    for sample in igoSamplesYear:
        data['x'].append(sample[1])
        data['y'].append(sample[0])
    return data





def getPiSamples():
    log_info("getting piSamples")

    piSamples_statement = "SELECT count(*) as samples,investigatorEmail  FROM samplestatus.sample GROUP BY investigatorEmail order by samples desc limit 10;"
    # piSamples_statement = "SELECT count(*),  MONTH(date), Year(date) FROM samplestatus.status GROUP BY YEAR(date), MONTH(date);"

    piSamples = engine.execute(piSamples_statement)
    data = {'values': [], 'labels': []}
    print(data['values'])
    for sample in piSamples:
        print(sample)
        data['values'].append(sample[0])
        data['labels'].append(sample[1])
    return data


def getTumorTypes():
    log_info("getting tumorTypes")

    tumorTypes_statement = "SELECT tumorOrNormal, count(*) FROM samplestatus.sample GROUP BY tumorOrNormal;"
    # tumorTypes_statement = "SELECT count(*),  MONTH(date), Year(date) FROM samplestatus.status GROUP BY YEAR(date), MONTH(date);"

    tumorTypes = engine.execute(tumorTypes_statement)
    data = {'x': [], 'y': []}
    for sample in tumorTypes:
        # print(sample)
        data['x'].append(sample[1])
        data['y'].append(sample[0])
    if data['y'][2] == '':
        data['y'][2] = 'n/a'
    return data


def getRoslinSamplesByYear():
    log_info("getting roslinSamplesByYear")

    getRoslinSamplesByYear_statement = "SELECT count(*),  YEAR(date) FROM samplestatus.status WHERE state = 'Roslin Done' GROUP BY YEAR(date);"
    # getRoslinSamplesByYear_statement = "SELECT count(*),  MONTH(date), Year(date) FROM samplestatus.status GROUP BY YEAR(date), MONTH(date);"

    getRoslinSamplesByYear = engine.execute(getRoslinSamplesByYear_statement)
    data = {'x': [], 'y': []}
    for sample in getRoslinSamplesByYear:
        data['x'].append(sample[1])
        data['y'].append(sample[0])
    return data


def getRoslinSamplesPast3():
    log_info("getting roslinSamplesPast3")

    roslinSamplesPast3_statement = "SELECT  month(date), count(*) FROM samplestatus.status WHERE state = 'Roslin Done' and  date >= DATE_ADD(NOW(), INTERVAL -3 MONTH)  GROUP BY month(date) ORDER BY MONTH(date);"
    # roslinSamplesPast3_statement = "SELECT count(*),  MONTH(date), Year(date) FROM samplestatus.status GROUP BY YEAR(date), MONTH(date);"

    roslinSamplesPast3 = engine.execute(roslinSamplesPast3_statement)
    data = {'x': [], 'y': []}
    for sample in roslinSamplesPast3:
        data['x'].append(calendar.month_abbr[sample[0]])
        data['y'].append(sample[1])
    return data



def getIGOSamplesPast3():
    log_info("getting roslinSamplesPast3")

    igoSamplesPast3_statement = "SELECT MONTH(date), count(*) FROM samplestatus.status WHERE state = 'IGO_RECEIVED' and  date >= DATE_ADD(NOW(), INTERVAL -3 MONTH) GROUP BY MONTH(date) ORDER BY MONTH(date);"
    # igoSamplesPast3_statement = "SELECT count(*),  MONTH(date), Year(date) FROM samplestatus.status GROUP BY YEAR(date), MONTH(date);"

    igoSamplesPast3 = engine.execute(igoSamplesPast3_statement)
    data = {'x': [], 'y': []}
    for sample in igoSamplesPast3:
        data['x'].append(calendar.month_abbr[sample[0]])
        data['y'].append(sample[1])
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
