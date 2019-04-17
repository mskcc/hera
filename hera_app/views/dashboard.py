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


@dashboard_blueprint.route("/dashboard")
@dashboard_blueprint.route("/")
@login_required
def dashboard():
    sampleCount = getSampleCount()
    igoSamplesYear = getIGOSamplesYear()
    igoSamplesPast3 = getIGOSamplesPast3()
    roslinSamplesPast3 = getRoslinSamplesPast3()
    roslinSamplesByYear = getRoslinSamplesByYear()
    piSamples = getPiSamples()
    tumorTypes = getTumorTypes()
    graphs = [
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
                )
            ],
            layout=dict(
                title='Roslin Samples Received By Year',
                autosize=False,
                width=500,
                height=500,
                xaxis=dict(nticks=len(roslinSamplesByYear['x']) + 1),
            ),
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
                    x=piSamples['labels'],
                    y=piSamples['values'],
                    type='bar',
                    marker=dict(color='#F6C65B'),
                )
            ],
            layout=dict(
                title='Top Ten PIs by Number of WES Samples',
                barmode='stack',
                autosize=False,
                width=500,
                height=500,
            ),
        ), 
        
        dict(
            data=[
                dict(
                    x=tumorTypes['labels'],
                    y=tumorTypes['values'],
                    type='bar',
                    marker=dict(color='#009490'),
                )
            ],
            layout=dict(
                title='Most Common Tumor Types',
                barmode='stack',
                autosize=False,
                width=500,
                height=500,
            ),
        ),

        # dict(
        #     data=[
        #         dict(
        #             labels=tumorTypes['y'],
        #             values=tumorTypes['x'],
        #             type='pie',
        #             marker=dict(color='#83276B'),
        #         )
        #     ],
        #     layout=dict(title='Tumor Types', autosize=False, width=500, height=500),
        # ),
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
    return render_template(
        '/dashboard.html', sampleCount=sampleCount, ids=ids, graphJSON=graphJSON
    )


def getSampleCount():
    sampleCount_statement = "SELECT count(*) FROM samplestatus.sample;"
    app.logger.info('total number of samples ' + sampleCount_statement)
    data = engine.execute(sampleCount_statement)
    return data.fetchone()[0]


def getIGOSamplesYear():
    igoSamplesYear_statement = "SELECT count(*),  Year(date) FROM samplestatus.status WHERE state = 'IGO_RECEIVED' GROUP BY YEAR(date);"
    app.logger.info('IGO samples by year ' + igoSamplesYear_statement)
    igoSamplesYear = engine.execute(igoSamplesYear_statement)
    data = {'x': [], 'y': []}
    for sample in igoSamplesYear:
        data['x'].append(sample[1])
        data['y'].append(sample[0])
    return data


def getPiSamples():
    piSamples_statement = "with top10 as (select  count(*)  as samples, investigator from samplestatus.sample GROUP BY investigator order by samples limit 10) select * from top10 union all select count(*), 'other' as investigator from samplestatus.sample where investigator not in (select investigator from top10);"
    # piSamplesOther_statement = "SELECT count(*) as samples,investigatorEmail  FROM samplestatus.sample GROUP BY investigatorEmail order by samples desc offset 10;"
    app.logger.info("getting piSamples: " + piSamples_statement)
    piSamples = engine.execute(piSamples_statement)
    data = {'values': [], 'labels': []}
    for sample in piSamples:
        data['values'].append(sample[0])
        data['labels'].append(sample[1])
    return data


def getTumorTypes():
    # tumorTypes_statement = "with top10 as (select  count(*)  as samples, tumorType from samplestatus.sample WHERE tumorType is not null and tumorType != '' and tumorType != 'Normal'   GROUP BY tumorType order by samples desc limit 10) select * from top10 union all select count(*), 'other' as tumorType from samplestatus.sample where tumorType not in (select tumorType from top10);"
    tumorTypes_statement = "select  count(*)  as samples, tumorType from samplestatus.sample WHERE tumorType is not null and tumorType != '' and tumorType != 'Normal'   GROUP BY tumorType Order by samples;"
    # tumorTypesOther_statement = "SELECT count(*) as samples,tumorTypeEmail  FROM samplestatus.sample GROUP BY investigatorEmail order by samples desc offset 10;"
    app.logger.info("getting tumorTypes: " + tumorTypes_statement)
    tumorTypes = engine.execute(tumorTypes_statement)
    data = {'values': [], 'labels': []}
    for sample in tumorTypes:
        data['values'].append(sample[0])
        data['labels'].append(sample[1])
    return data

# piechart
# def getTumorTypes():
#     tumorTypes_statement = "SELECT tumorOrNormal, count(*) FROM samplestatus.sample GROUP BY tumorOrNormal;"
#     app.logger.info("getting tumorTypes: " + tumorTypes_statement)
#     tumorTypes = engine.execute(tumorTypes_statement)
#     data = {'x': [], 'y': []}
#     for sample in tumorTypes:
#         data['x'].append(sample[1])
#         data['y'].append(sample[0])
#     if data['y'][2] == '':
#         data['y'][2] = 'n/a'
#     return data


def getRoslinSamplesByYear():
    getRoslinSamplesByYear_statement = "SELECT count(*),  YEAR(date) FROM samplestatus.status WHERE state = 'Roslin Done' GROUP BY YEAR(date);"
    app.logger.info("getting roslinSamplesByYear: " + getRoslinSamplesByYear_statement)
    getRoslinSamplesByYear = engine.execute(getRoslinSamplesByYear_statement)
    data = {'x': [], 'y': []}
    for sample in getRoslinSamplesByYear:
        data['x'].append(sample[1])
        data['y'].append(sample[0])
    return data


def getRoslinSamplesPast3():
    roslinSamplesPast3_statement = "SELECT  month(date), count(*) FROM samplestatus.status WHERE state = 'Roslin Done' and  date >= DATE_ADD(NOW(), INTERVAL -3 MONTH)  GROUP BY month(date) ORDER BY MONTH(date);"
    app.logger.info("getting roslinSamplesPast3: " + roslinSamplesPast3_statement)
    roslinSamplesPast3 = engine.execute(roslinSamplesPast3_statement)
    data = {'x': [], 'y': []}
    for sample in roslinSamplesPast3:
        data['x'].append(calendar.month_abbr[sample[0]])
        data['y'].append(sample[1])
    return data


def getIGOSamplesPast3():
    igoSamplesPast3_statement = "SELECT MONTH(date), count(*) FROM samplestatus.status WHERE state = 'IGO_RECEIVED' and  date >= DATE_ADD(NOW(), INTERVAL -3 MONTH) GROUP BY MONTH(date) ORDER BY MONTH(date);"
    app.logger.info("getting igoSamplesPast3: " + igoSamplesPast3_statement)
    igoSamplesPast3 = engine.execute(igoSamplesPast3_statement)
    data = {'x': [], 'y': []}
    for sample in igoSamplesPast3:
        data['x'].append(calendar.month_abbr[sample[0]])
        data['y'].append(sample[1])
    return data
