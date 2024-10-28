from application import app
from application import db
from application.models import Portfolio
from application.models import watchlist
from flask import render_template, request, jsonify, redirect, url_for, send_from_directory,flash
from application.forms import RegistrationForm, LoginForm
from application.models import Users
from flask_login import login_user, current_user, login_required, logout_user
import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import numpy as np

import requests


import plotly.graph_objects as go

def create_plot(df, period):
    if period == '1M':
        filtered_data = df.last('1M')
    elif period == '1Y':
        filtered_data = df.last('1Y')
    elif period == '5Y':
        filtered_data = df.last('5Y')
    elif period == 'All':
        filtered_data = df
    else:
        raise ValueError("Invalid period specified")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=filtered_data.index,
        y=filtered_data['Close'],
        mode='lines',
        fill='tozeroy',
        line=dict(color='green'),
        fillcolor='white',
        name='Close Price'
    ))

    fig.update_layout(
        title=f' {period}',
        xaxis_title='Date',
        yaxis_title='Price',
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        width=800,
        height=500,
        xaxis=dict(showgrid=False, showline=False),
        yaxis=dict(showgrid=False, showline=False)
    )

    return fig


#stock newses
@app.route('/suzlon-news')
def suzlon_news():
    api_key = '825abcd9a5bc4382b113e4108f29968c'
    url = f'https://newsapi.org/v2/everything?q=Suzlon&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    return jsonify(news_data)



@app.route('/mrf-news')
def mrf_news():
    api_key = '825abcd9a5bc4382b113e4108f29968c'
    url = f'https://newsapi.org/v2/everything?q=MRF Ltd&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    return jsonify(news_data)

@app.route('/infosys-news')
def infosys_news():
    api_key = '825abcd9a5bc4382b113e4108f29968c'
    url = f'https://newsapi.org/v2/everything?q=INFOSYS&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    return jsonify(news_data)

@app.route('/tata_motors-news')
def tata_motors_news():
    api_key = '825abcd9a5bc4382b113e4108f29968c'
    url = f'https://newsapi.org/v2/everything?q=TATAMOTORS&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    return jsonify(news_data)


@app.route('/reliance_power-news')
def reliance_power_news():
    api_key = '825abcd9a5bc4382b113e4108f29968c'
    url = f'https://newsapi.org/v2/everything?q=RELIANCE&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    return jsonify(news_data)

@app.route('/adani_green-news')
def adani_green_news():
    api_key = '825abcd9a5bc4382b113e4108f29968c'
    url = f'https://newsapi.org/v2/everything?q=Adani&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    return jsonify(news_data)

@app.route('/airtel-news')
def airtel_news():
    api_key = '825abcd9a5bc4382b113e4108f29968c'
    url = f'https://newsapi.org/v2/everything?q=AIRTEL&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    return jsonify(news_data)

@app.route('/titan-news')
def titan_news():
    api_key = '825abcd9a5bc4382b113e4108f29968c'
    url = f'https://newsapi.org/v2/everything?q=TITAN&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    return jsonify(news_data)

@app.route('/zomato-news')
def zomato_news():
    api_key = '825abcd9a5bc4382b113e4108f29968c'
    url = f'https://newsapi.org/v2/everything?q=zomato&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    return jsonify(news_data)

@app.route('/yesbank-news')
def yesbank_news():
    api_key = '825abcd9a5bc4382b113e4108f29968c'
    url = f'https://newsapi.org/v2/everything?q=BANKshares&apiKey={api_key}'
    response = requests.get(url)
    news_data = response.json()
    return jsonify(news_data)


#stock visulization routes

@app.route('/suzlon/<period>')
def suzlon(period):
    df = pd.read_csv('suzlonall.csv', parse_dates=True, index_col='Date', dayfirst=True)
    df.index = pd.to_datetime(df.index, format='%d-%m-%Y')
    fig = create_plot(df, period)
    graph_json = pio.to_json(fig)
    return jsonify(graph_json)


@app.route('/mrf/<period>')
def mrf(period):
    df = pd.read_csv('mrf.csv', parse_dates=True, index_col='Date', dayfirst=True)
    df.index = pd.to_datetime(df.index, format='%d-%m-%Y')
    fig = create_plot(df, period)
    graph_json = pio.to_json(fig)
    return jsonify(graph_json)


@app.route('/infosys/<period>')
def infosys(period):
    df = pd.read_csv('infosys.csv', parse_dates=True, index_col='Date', dayfirst=True)
    df.index = pd.to_datetime(df.index, format='%d-%m-%Y')
    fig = create_plot(df, period)
    graph_json = pio.to_json(fig)
    return jsonify(graph_json)



@app.route('/tata_motors/<period>')
def tata_motors(period):
    df = pd.read_csv('tata.csv', parse_dates=True, index_col='Date', dayfirst=True)
    df.index = pd.to_datetime(df.index, format='%d-%m-%Y')
    fig = create_plot(df, period)
    graph_json = pio.to_json(fig)
    return jsonify(graph_json)


@app.route('/reliance_power/<period>')
def reliance_power(period):
    df = pd.read_csv('Rpower.csv', parse_dates=True, index_col='Date', dayfirst=True)
    df.index = pd.to_datetime(df.index, format='%d-%m-%Y')
    fig = create_plot(df, period)
    graph_json = pio.to_json(fig)
    return jsonify(graph_json)


@app.route('/adani_green/<period>')
def adani_green(period):
    df = pd.read_csv('adanigreen.csv', parse_dates=True, index_col='Date', dayfirst=True)
    df.index = pd.to_datetime(df.index, format='%d-%m-%Y')
    fig = create_plot(df, period)
    graph_json = pio.to_json(fig)
    return jsonify(graph_json)

@app.route('/airtel/<period>')
def airtel(period):
    df = pd.read_csv('airtel.csv', parse_dates=True, index_col='Date', dayfirst=True)
    df.index = pd.to_datetime(df.index, format='%d-%m-%Y')
    fig = create_plot(df, period)
    graph_json = pio.to_json(fig)
    return jsonify(graph_json)

@app.route('/titan/<period>')
def titan(period):
    df = pd.read_csv('titan.csv', parse_dates=True, index_col='Date', dayfirst=True)
    df.index = pd.to_datetime(df.index, format='%d-%m-%Y')
    fig = create_plot(df, period)
    graph_json = pio.to_json(fig)
    return jsonify(graph_json)

@app.route('/zomato/<period>')
def zomato(period):
    df = pd.read_csv('zomato.csv', parse_dates=True, index_col='Date', dayfirst=True)
    df.index = pd.to_datetime(df.index, format='%d-%m-%Y')
    fig = create_plot(df, period)
    graph_json = pio.to_json(fig)
    return jsonify(graph_json)

@app.route('/yesbank/<period>')
def yesbank(period):
    df = pd.read_csv('yesbank.csv', parse_dates=True, index_col='Date', dayfirst=True)
    df.index = pd.to_datetime(df.index, format='%d-%m-%Y')
    fig = create_plot(df, period)
    graph_json = pio.to_json(fig)
    return jsonify(graph_json)


