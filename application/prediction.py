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
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from datetime import datetime
import json
import plotly
import requests

import plotly.graph_objects as go


def create_sequences(data, sequence_length):
    sequences = []
    for i in range(len(data) - sequence_length):
        sequences.append(data[i:i + sequence_length])
    return np.array(sequences)



def build_and_train_model(X_train, y_train):
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=1, batch_size=12, validation_split=0.1)
    return model



def make_predictions(model, X_test, scaler):
    predicted_prices = model.predict(X_test)
    predicted_prices = scaler.inverse_transform(predicted_prices)
    return predicted_prices



def predict_future_prices(model, last_sequence, scaler, future_days=30):
    future_predictions = []
    current_sequence = last_sequence.reshape((1, last_sequence.shape[0], 1))
    for _ in range(future_days):
        next_pred = model.predict(current_sequence)
        future_predictions.append(next_pred[0, 0])
        current_sequence = np.append(current_sequence[:, 1:, :], [[[next_pred[0, 0]]]], axis=1)
    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 1))
    return future_predictions





def process_suzlon_data():
    data = pd.read_csv('suzlonall.CSV', parse_dates=['Date'], dayfirst=True)
    data.set_index('Date', inplace=True)
    closing_prices = data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(closing_prices)
    return data, scaled_data, scaler



def process_mrf_data():
    data = pd.read_csv('mrf.CSV', parse_dates=['Date'], dayfirst=True)
    data.set_index('Date', inplace=True)
    closing_prices = data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(closing_prices)
    return data, scaled_data, scaler

def process_infosys_data():
    data = pd.read_csv('infosys.CSV', parse_dates=['Date'], dayfirst=True)
    data.set_index('Date', inplace=True)
    closing_prices = data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(closing_prices)
    return data, scaled_data, scaler

def process_tata_motors_data():
    data = pd.read_csv('tata.CSV', parse_dates=['Date'], dayfirst=True)
    data.set_index('Date', inplace=True)
    closing_prices = data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(closing_prices)
    return data, scaled_data, scaler


def process_reliance_power_data():
    data = pd.read_csv('Rpower.CSV', parse_dates=['Date'], dayfirst=True)
    data.set_index('Date', inplace=True)
    closing_prices = data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(closing_prices)
    return data, scaled_data, scaler

def process_adani_green_data():
    data= pd.read_csv('adanigreen.csv',parse_dates=['Date'],dayfirst=True)
    data.set_index('Date',inplace=True)
    closing_prices = data['Close'].values.reshape(-1,1)
    scaler = MinMaxScaler(feature_range=(0,1))
    scaler_data =scaler.fit_transform(closing_prices)
    return data,scaler_data,scaler

def process_airtel_data():
    data= pd.read_csv('airtel.csv',parse_dates=['Date'],dayfirst=True)
    data.set_index('Date',inplace=True)
    closing_prices = data['Close'].values.reshape(-1,1)
    scaler = MinMaxScaler(feature_range=(0,1))
    scaler_data =scaler.fit_transform(closing_prices)
    return data,scaler_data,scaler

def process_titan_data():
    data= pd.read_csv('titan.csv',parse_dates=['Date'],dayfirst=True)
    data.set_index('Date',inplace=True)
    closing_prices = data['Close'].values.reshape(-1,1)
    scaler = MinMaxScaler(feature_range=(0,1))
    scaler_data =scaler.fit_transform(closing_prices)
    return data,scaler_data,scaler

def process_zomato_data():
    data= pd.read_csv('zomato.csv',parse_dates=['Date'],dayfirst=True)
    data.set_index('Date',inplace=True)
    closing_prices = data['Close'].values.reshape(-1,1)
    scaler = MinMaxScaler(feature_range=(0,1))
    scaler_data =scaler.fit_transform(closing_prices)
    return data,scaler_data,scaler

def process_yesbank_data():
    data= pd.read_csv('yesbank.csv',parse_dates=['Date'],dayfirst=True)
    data.set_index('Date',inplace=True)
    closing_prices = data['Close'].values.reshape(-1,1)
    scaler = MinMaxScaler(feature_range=(0,1))
    scaler_data =scaler.fit_transform(closing_prices)
    return data,scaler_data,scaler

#stock future predictions

@app.route('/predictsuzlon')
def predict_suzlon():
    data, scaled_data, scaler = process_suzlon_data()
    sequence_length = 60
    sequences = create_sequences(scaled_data, sequence_length)
    X = sequences[:, :-1]
    y = sequences[:, -1]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    train_size = int(X.shape[0] * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    model = build_and_train_model(X_train, y_train)
    predicted_prices = make_predictions(model, X_test, scaler)
    last_sequence = scaled_data[-sequence_length:]
    future_predictions = predict_future_prices(model, last_sequence, scaler)
    future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=30)

    # Prepare data for Plotly
    actual_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=data['Close'].values[-len(predicted_prices):], mode='lines', name='Actual Price')
    predicted_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=predicted_prices.flatten(), mode='lines', name='Predicted Price')
    future_trace = go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='Future Predictions')

    layout = go.Layout(title='Stock Price Prediction', xaxis={'title': 'Date'}, yaxis={'title': 'Stock Price'})
    fig = go.Figure(data=[actual_trace, predicted_trace, future_trace], layout=layout)

    return jsonify(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))




@app.route('/predictmrf')
def predict_mrf():
    data, scaled_data, scaler = process_mrf_data()
    sequence_length = 60
    sequences = create_sequences(scaled_data, sequence_length)
    X = sequences[:, :-1]
    y = sequences[:, -1]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    train_size = int(X.shape[0] * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    model = build_and_train_model(X_train, y_train)
    predicted_prices = make_predictions(model, X_test, scaler)
    last_sequence = scaled_data[-sequence_length:]
    future_predictions = predict_future_prices(model, last_sequence, scaler)
    future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=30)

    # Prepare data for Plotly
    actual_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=data['Close'].values[-len(predicted_prices):], mode='lines', name='Actual Price')
    predicted_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=predicted_prices.flatten(), mode='lines', name='Predicted Price')
    future_trace = go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='Future Predictions')

    layout = go.Layout(title='Stock Price Prediction', xaxis={'title': 'Date'}, yaxis={'title': 'Stock Price'})
    fig = go.Figure(data=[actual_trace, predicted_trace, future_trace], layout=layout)

    return jsonify(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


@app.route('/predict_infosys')
def predict_infosys():
    data, scaled_data, scaler = process_infosys_data()
    sequence_length = 60
    sequences = create_sequences(scaled_data, sequence_length)
    X = sequences[:, :-1]
    y = sequences[:, -1]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    train_size = int(X.shape[0] * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    model = build_and_train_model(X_train, y_train)
    predicted_prices = make_predictions(model, X_test, scaler)
    last_sequence = scaled_data[-sequence_length:]
    future_predictions = predict_future_prices(model, last_sequence, scaler)
    future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=30)

    # Prepare data for Plotly
    actual_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=data['Close'].values[-len(predicted_prices):], mode='lines', name='Actual Price')
    predicted_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=predicted_prices.flatten(), mode='lines', name='Predicted Price')
    future_trace = go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='Future Predictions')

    layout = go.Layout(title='Stock Price Prediction', xaxis={'title': 'Date'}, yaxis={'title': 'Stock Price'})
    fig = go.Figure(data=[actual_trace, predicted_trace, future_trace], layout=layout)

    return jsonify(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))


@app.route('/predict_tata_motors')
def predict_tata_motors():
    data, scaled_data, scaler = process_tata_motors_data()
    sequence_length = 60
    sequences = create_sequences(scaled_data, sequence_length)
    X = sequences[:, :-1]
    y = sequences[:, -1]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    train_size = int(X.shape[0] * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    model = build_and_train_model(X_train, y_train)
    predicted_prices = make_predictions(model, X_test, scaler)
    last_sequence = scaled_data[-sequence_length:]
    future_predictions = predict_future_prices(model, last_sequence, scaler)
    future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=30)

    # Prepare data for Plotly
    actual_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=data['Close'].values[-len(predicted_prices):], mode='lines', name='Actual Price')
    predicted_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=predicted_prices.flatten(), mode='lines', name='Predicted Price')
    future_trace = go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='Future Predictions')

    layout = go.Layout(title='Stock Price Prediction', xaxis={'title': 'Date'}, yaxis={'title': 'Stock Price'})
    fig = go.Figure(data=[actual_trace, predicted_trace, future_trace], layout=layout)

    return jsonify(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

@app.route('/predict_rpower')
def predict_rpower():
    data, scaled_data, scaler = process_reliance_power_data()
    sequence_length = 60
    sequences = create_sequences(scaled_data, sequence_length)
    X = sequences[:, :-1]
    y = sequences[:, -1]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    train_size = int(X.shape[0] * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    model = build_and_train_model(X_train, y_train)
    predicted_prices = make_predictions(model, X_test, scaler)
    last_sequence = scaled_data[-sequence_length:]
    future_predictions = predict_future_prices(model, last_sequence, scaler)
    future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=30)

    # Prepare data for Plotly
    actual_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=data['Close'].values[-len(predicted_prices):], mode='lines', name='Actual Price')
    predicted_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=predicted_prices.flatten(), mode='lines', name='Predicted Price')
    future_trace = go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='Future Predictions')

    layout = go.Layout(title='Stock Price Prediction', xaxis={'title': 'Date'}, yaxis={'title': 'Stock Price'})
    fig = go.Figure(data=[actual_trace, predicted_trace, future_trace], layout=layout)

    return jsonify(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

@app.route('/predict_adani_green')
def predict_adani_green():
    data, scaled_data, scaler = process_adani_green_data()
    sequence_length = 60
    sequences = create_sequences(scaled_data, sequence_length)
    X = sequences[:, :-1]
    y = sequences[:, -1]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    train_size = int(X.shape[0] * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    model = build_and_train_model(X_train, y_train)
    predicted_prices = make_predictions(model, X_test, scaler)
    last_sequence = scaled_data[-sequence_length:]
    future_predictions = predict_future_prices(model, last_sequence, scaler)
    future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=15)

    # Prepare data for Plotly
    actual_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=data['Close'].values[-len(predicted_prices):], mode='lines', name='Actual Price')
    predicted_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=predicted_prices.flatten(), mode='lines', name='Predicted Price')
    future_trace = go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='Future Predictions')

    layout = go.Layout(title='Stock Price Prediction', xaxis={'title': 'Date'}, yaxis={'title': 'Stock Price'})
    fig = go.Figure(data=[actual_trace, predicted_trace, future_trace], layout=layout)

    return jsonify(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

@app.route('/predict_airtel')
def predict_airtel():
    data, scaled_data, scaler = process_airtel_data()
    sequence_length = 60
    sequences = create_sequences(scaled_data, sequence_length)
    X = sequences[:, :-1]
    y = sequences[:, -1]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    train_size = int(X.shape[0] * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    model = build_and_train_model(X_train, y_train)
    predicted_prices = make_predictions(model, X_test, scaler)
    last_sequence = scaled_data[-sequence_length:]
    future_predictions = predict_future_prices(model, last_sequence, scaler)
    future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=15)

    # Prepare data for Plotly
    actual_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=data['Close'].values[-len(predicted_prices):], mode='lines', name='Actual Price')
    predicted_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=predicted_prices.flatten(), mode='lines', name='Predicted Price')
    future_trace = go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='Future Predictions')

    layout = go.Layout(title='Stock Price Prediction', xaxis={'title': 'Date'}, yaxis={'title': 'Stock Price'})
    fig = go.Figure(data=[actual_trace, predicted_trace, future_trace], layout=layout)

    return jsonify(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

@app.route('/predict_titan')
def predict_titan():
    data, scaled_data, scaler = process_titan_data()
    sequence_length = 60
    sequences = create_sequences(scaled_data, sequence_length)
    X = sequences[:, :-1]
    y = sequences[:, -1]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    train_size = int(X.shape[0] * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    model = build_and_train_model(X_train, y_train)
    predicted_prices = make_predictions(model, X_test, scaler)
    last_sequence = scaled_data[-sequence_length:]
    future_predictions = predict_future_prices(model, last_sequence, scaler)
    future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=15)

    # Prepare data for Plotly
    actual_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=data['Close'].values[-len(predicted_prices):], mode='lines', name='Actual Price')
    predicted_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=predicted_prices.flatten(), mode='lines', name='Predicted Price')
    future_trace = go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='Future Predictions')

    layout = go.Layout(title='Stock Price Prediction', xaxis={'title': 'Date'}, yaxis={'title': 'Stock Price'})
    fig = go.Figure(data=[actual_trace, predicted_trace, future_trace], layout=layout)

    return jsonify(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

@app.route('/predict_zomato')
def predict_zomato():
    data, scaled_data, scaler = process_zomato_data()
    sequence_length = 60
    sequences = create_sequences(scaled_data, sequence_length)
    X = sequences[:, :-1]
    y = sequences[:, -1]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    train_size = int(X.shape[0] * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    model = build_and_train_model(X_train, y_train)
    predicted_prices = make_predictions(model, X_test, scaler)
    last_sequence = scaled_data[-sequence_length:]
    future_predictions = predict_future_prices(model, last_sequence, scaler)
    future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=15)

    # Prepare data for Plotly
    actual_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=data['Close'].values[-len(predicted_prices):], mode='lines', name='Actual Price')
    predicted_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=predicted_prices.flatten(), mode='lines', name='Predicted Price')
    future_trace = go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='Future Predictions')

    layout = go.Layout(title='Stock Price Prediction', xaxis={'title': 'Date'}, yaxis={'title': 'Stock Price'})
    fig = go.Figure(data=[actual_trace, predicted_trace, future_trace], layout=layout)

    return jsonify(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

@app.route('/predict_yesbank')
def predict_yesbank():
    data, scaled_data, scaler = process_yesbank_data()
    sequence_length = 60
    sequences = create_sequences(scaled_data, sequence_length)
    X = sequences[:, :-1]
    y = sequences[:, -1]
    X = X.reshape(X.shape[0], X.shape[1], 1)
    train_size = int(X.shape[0] * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    model = build_and_train_model(X_train, y_train)
    predicted_prices = make_predictions(model, X_test, scaler)
    last_sequence = scaled_data[-sequence_length:]
    future_predictions = predict_future_prices(model, last_sequence, scaler)
    future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=15)

    # Prepare data for Plotly
    actual_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=data['Close'].values[-len(predicted_prices):], mode='lines', name='Actual Price')
    predicted_trace = go.Scatter(x=data.index[-len(predicted_prices):], y=predicted_prices.flatten(), mode='lines', name='Predicted Price')
    future_trace = go.Scatter(x=future_dates, y=future_predictions.flatten(), mode='lines', name='Future Predictions')

    layout = go.Layout(title='Stock Price Prediction', xaxis={'title': 'Date'}, yaxis={'title': 'Stock Price'})
    fig = go.Figure(data=[actual_trace, predicted_trace, future_trace], layout=layout)

    return jsonify(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))

