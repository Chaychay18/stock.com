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

from datetime import datetime


# Define routes
@app.route('/')
@app.route('/home')
def home_page():
    return render_template('index.html')


@app.route('/reg', methods=['GET', 'POST'])
def reg_page():
    form = RegistrationForm()
    if request.method == "POST" and form.validate_on_submit():
        # Registration logic here

        first_name = form.first_name.data
        last_name = form.last_name.data
        phone_number = form.phone_number.data
        email_address = form.email_address.data
        pan_number = form.pan_number.data
        password = form.password1.data

        existing_user = Users.query.filter_by(email_address=email_address).first()
        number = Users.query.filter_by(phone_number=phone_number).first()
        if existing_user:
            return jsonify({"status": "email"})
        if number:
            return jsonify({"status": "phone"})

        new_user = Users(
            first_name=first_name,
            last_name=last_name,
            email_address=email_address,
            phone_number=phone_number,
            pan_number=pan_number,
            password=password,
            wallet=2000
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"status": "success"})
     
    return render_template('reg.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        attempted_user = Users.query.filter_by(email_address=form.email_address.data).first()
        if attempted_user and attempted_user.check_password(attempted_password=form.password.data):
            login_user(attempted_user)
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "fail", "message": "Invalid email or password"})

    return render_template('login.html', form=form)



@app.route('/dashboard')
@login_required
def dashboard():
    wallet_amount = float(current_user.wallet)
    return render_template('dashboard.html',wallet_amount=wallet_amount)


@app.route('/profile')
@login_required
def profile_dashboard():    
    if current_user.is_authenticated:
        first_name = current_user.first_name
        last_name = current_user.last_name
        email_address = current_user.email_address
        phone_number = current_user.phone_number
        pan_number = current_user.pan_number
        wallet_amount = current_user.wallet
        
        return render_template('profile2.html', 
                               first_name=first_name,
                               last_name = last_name,
                               email_address=email_address,
                               phone_number = phone_number,
                               pan_number = pan_number,
                               wallet_amount=wallet_amount
                               )
    else:
        return redirect(url_for('/login'))
    



@app.route('/success')
def success_page():
    return render_template('success.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home_page'))




@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)




@app.route('/about')
def about():
    return render_template('about.html')




@app.route('/service')
def service():
    return render_template('service.html')



@app.route('/stocks')
@login_required
def stocks():
    return render_template('stocks.html')

#prediction functions


#stock company details

@app.route('/company-overview')
def company_overview():
    # Replace with your actual company details or fetch from a database
    company_details = {
        "details": "Suzlon Energy is a wind turbine supplier based in Pune, India. It was formerly ranked by MAKE as the fifth largest wind turbine supplier in the world."
    }
    return jsonify(company_details)


#stock news routes







#stock page routes
@app.route('/suzlon', methods=['GET', 'POST'])
@login_required
def suzlon_page():
    current_price = 48
    stock_name = "Suzlon Energy"
    wallet_amount = float(current_user.wallet)
    
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        action = request.form.get('action')
        
        if action == 'buy':
            total_cost = current_price * quantity
            
            if total_cost > wallet_amount:
                flash('Not enough funds in wallet to complete purchase', 'danger')
            else:
                current_user.wallet -= total_cost
                db.session.commit()
                
                new_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=quantity,
                    total_cost=total_cost,
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='buy'
                )
                db.session.add(new_stock)
                db.session.commit()
                
                flash(f'You bought {quantity} {stock_name} stocks for {total_cost} successfully!', 'success')
        
        elif action == 'sell':
            # Check if the user has enough stocks to sell
            total_purchased_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='buy').scalar() or 0
            total_sold_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='sell').scalar() or 0
            available_quantity = total_purchased_quantity - total_sold_quantity
            
            if available_quantity <= 0:
                flash('Not enough stocks to sell', 'danger')
            elif quantity > available_quantity:
                flash('Quantity exceeds available stocks', 'danger')
            else:
                total_gain = current_price * quantity
                total_cost = current_price * quantity  # Correct the total cost

                current_user.wallet += total_gain
                db.session.commit()

                sold_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=-quantity,  # Negative quantity for sold stocks
                    total_cost=-total_cost,  # Negative total cost
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='sell'
                )
                db.session.add(sold_stock)
                db.session.commit()

                flash(f'You sold {quantity} {stock_name} stocks for {total_gain} successfully!', 'success')
                
        return redirect(url_for('suzlon_page'))
    
    return render_template('suzlon.html', current_price=current_price, stock_name=stock_name, wallet_amount=wallet_amount)



@app.route('/mrf', methods=['GET', 'POST'])
@login_required
def mrf_page():
    current_price = 125
    stock_name = "MRF Ltd."
    wallet_amount = float(current_user.wallet)
    
       
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        action = request.form.get('action')
        
        if action == 'buy':
            total_cost = current_price * quantity
            
            if total_cost > wallet_amount:
                flash('Not enough funds in wallet to complete purchase', 'danger')
            else:
                current_user.wallet -= total_cost
                db.session.commit()
                
                new_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=quantity,
                    total_cost=total_cost,
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='buy'
                )
                db.session.add(new_stock)
                db.session.commit()
                
                flash(f'You bought {quantity} {stock_name} stocks for {total_cost} successfully!', 'success')
        
        elif action == 'sell':
            # Check if the user has enough stocks to sell
            total_purchased_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='buy').scalar() or 0
            total_sold_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='sell').scalar() or 0
            available_quantity = total_purchased_quantity - total_sold_quantity
            
            if available_quantity <= 0:
                flash('Not enough stocks to sell', 'danger')
            elif quantity > available_quantity:
                flash('Quantity exceeds available stocks', 'danger')
            else:
                total_gain = current_price * quantity
                total_cost = current_price * quantity  # Correct the total cost

                current_user.wallet += total_gain
                db.session.commit()

                sold_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=-quantity,  # Negative quantity for sold stocks
                    total_cost=-total_cost,  # Negative total cost
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='sell'
                )
                db.session.add(sold_stock)
                db.session.commit()

                flash(f'You sold {quantity} {stock_name} stocks for {total_gain} successfully!', 'success')
                
        return redirect(url_for('portfolio'))
    
    return render_template('mrf.html', current_price=current_price, stock_name=stock_name, wallet_amount=wallet_amount)




@app.route('/infosys',methods=['GET','POST'])
@login_required
def infosys_page():
    current_price = 1450
    stock_name = "Infosys"
    wallet_amount = float(current_user.wallet)
    
       
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        action = request.form.get('action')
        
        if action == 'buy':
            total_cost = current_price * quantity
            
            if total_cost > wallet_amount:
                flash('Not enough funds in wallet to complete purchase', 'danger')
            else:
                current_user.wallet -= total_cost
                db.session.commit()
                
                new_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=quantity,
                    total_cost=total_cost,
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='buy'
                )
                db.session.add(new_stock)
                db.session.commit()
                
                flash(f'You bought {quantity} {stock_name} stocks for {total_cost} successfully!', 'success')
        
        elif action == 'sell':
            # Check if the user has enough stocks to sell
            total_purchased_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='buy').scalar() or 0
            total_sold_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='sell').scalar() or 0
            available_quantity = total_purchased_quantity - total_sold_quantity
            
            if available_quantity <= 0:
                flash('Not enough stocks to sell', 'danger')
            elif quantity > available_quantity:
                flash('Quantity exceeds available stocks', 'danger')
            else:
                total_gain = current_price * quantity
                total_cost = current_price * quantity  # Correct the total cost

                current_user.wallet += total_gain
                db.session.commit()

                sold_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=-quantity,  # Negative quantity for sold stocks
                    total_cost=-total_cost,  # Negative total cost
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='sell'
                )
                db.session.add(sold_stock)
                db.session.commit()

                flash(f'You sold {quantity} {stock_name} stocks for {total_gain} successfully!', 'success')
                
        return redirect(url_for('infosys_page'))
    
    return render_template('infosys.html', current_price=current_price, stock_name=stock_name, wallet_amount=wallet_amount)





@app.route('/tata_motors_page',methods=['GET','POST'])
@login_required
def tata_motors_page():
    current_price = 956
    stock_name = "TATA MOTORS."
    wallet_amount = float(current_user.wallet)
    
       
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        action = request.form.get('action')
        
        if action == 'buy':
            total_cost = current_price * quantity
            
            if total_cost > wallet_amount:
                flash('Not enough funds in wallet to complete purchase', 'danger')
            else:
                current_user.wallet -= total_cost
                db.session.commit()
                
                new_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=quantity,
                    total_cost=total_cost,
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='buy'
                )
                db.session.add(new_stock)
                db.session.commit()
                
                flash(f'You bought {quantity} {stock_name} stocks for {total_cost} successfully!', 'success')
        
        elif action == 'sell':
            # Check if the user has enough stocks to sell
            total_purchased_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='buy').scalar() or 0
            total_sold_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='sell').scalar() or 0
            available_quantity = total_purchased_quantity - total_sold_quantity
            
            if available_quantity <= 0:
                flash('Not enough stocks to sell', 'danger')
            elif quantity > available_quantity:
                flash('Quantity exceeds available stocks', 'danger')
            else:
                total_gain = current_price * quantity
                total_cost = current_price * quantity  # Correct the total cost

                current_user.wallet += total_gain
                db.session.commit()

                sold_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=-quantity,  # Negative quantity for sold stocks
                    total_cost=-total_cost,  # Negative total cost
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='sell'
                )
                db.session.add(sold_stock)
                db.session.commit()

                flash(f'You sold {quantity} {stock_name} stocks for {total_gain} successfully!', 'success')
                
        return redirect(url_for('tata_motors_page'))
    
    return render_template('tata_motors.html', current_price=current_price, stock_name=stock_name, wallet_amount=wallet_amount)





@app.route('/rpower',methods=['GET','POST'])
@login_required
def rpower_page():
    current_price = 22
    stock_name = "RELIANCE POWER"
    wallet_amount = float(current_user.wallet)
    
       
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        action = request.form.get('action')
        
        if action == 'buy':
            total_cost = current_price * quantity
            
            if total_cost > wallet_amount:
                flash('Not enough funds in wallet to complete purchase', 'danger')
            else:
                current_user.wallet -= total_cost
                db.session.commit()
                
                new_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=quantity,
                    total_cost=total_cost,
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='buy'
                )
                db.session.add(new_stock)
                db.session.commit()
                
                flash(f'You bought {quantity} {stock_name} stocks for {total_cost} successfully!', 'success')
        
        elif action == 'sell':
            # Check if the user has enough stocks to sell
            total_purchased_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='buy').scalar() or 0
            total_sold_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='sell').scalar() or 0
            available_quantity = total_purchased_quantity - total_sold_quantity
            
            if available_quantity <= 0:
                flash('Not enough stocks to sell', 'danger')
            elif quantity > available_quantity:
                flash('Quantity exceeds available stocks', 'danger')
            else:
                total_gain = current_price * quantity
                total_cost = current_price * quantity  # Correct the total cost

                current_user.wallet += total_gain
                db.session.commit()

                sold_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=-quantity,  # Negative quantity for sold stocks
                    total_cost=-total_cost,  # Negative total cost
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='sell'
                )
                db.session.add(sold_stock)
                db.session.commit()

                flash(f'You sold {quantity} {stock_name} stocks for {total_gain} successfully!', 'success')
                
        return redirect(url_for('rpower_page'))
    
    return render_template('reliance_power.html', current_price=current_price, stock_name=stock_name, wallet_amount=wallet_amount)





@app.route('/adani_green',methods=['GET','POST'])
@login_required
def adani_green_page():
    current_price = 1874
    stock_name = "Adani green"
    wallet_amount = float(current_user.wallet)
    
       
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        action = request.form.get('action')
        
        if action == 'buy':
            total_cost = current_price * quantity
            
            if total_cost > wallet_amount:
                flash('Not enough funds in wallet to complete purchase', 'danger')
            else:
                current_user.wallet -= total_cost
                db.session.commit()
                
                new_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=quantity,
                    total_cost=total_cost,
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='buy'
                )
                db.session.add(new_stock)
                db.session.commit()
                
                flash(f'You bought {quantity} {stock_name} stocks for {total_cost} successfully!', 'success')
        
        elif action == 'sell':
            # Check if the user has enough stocks to sell
            total_purchased_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='buy').scalar() or 0
            total_sold_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='sell').scalar() or 0
            available_quantity = total_purchased_quantity - total_sold_quantity
            
            if available_quantity <= 0:
                flash('Not enough stocks to sell', 'danger')
            elif quantity > available_quantity:
                flash('Quantity exceeds available stocks', 'danger')
            else:
                total_gain = current_price * quantity
                total_cost = current_price * quantity  # Correct the total cost

                current_user.wallet += total_gain
                db.session.commit()

                sold_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=-quantity,  # Negative quantity for sold stocks
                    total_cost=-total_cost,  # Negative total cost
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='sell'
                )
                db.session.add(sold_stock)
                db.session.commit()

                flash(f'You sold {quantity} {stock_name} stocks for {total_gain} successfully!', 'success')
                
        return redirect(url_for('adani_green_page'))
    
    return render_template('adani_green.html', current_price=current_price, stock_name=stock_name, wallet_amount=wallet_amount)





@app.route('/airtle',methods=['GET','POST'])
@login_required
def airtel_page():
    current_price = 1377
    stock_name = "Bharathi airtel"
    wallet_amount = float(current_user.wallet)
    
       
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        action = request.form.get('action')
        
        if action == 'buy':
            total_cost = current_price * quantity
            
            if total_cost > wallet_amount:
                flash('Not enough funds in wallet to complete purchase', 'danger')
            else:
                current_user.wallet -= total_cost
                db.session.commit()
                
                new_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=quantity,
                    total_cost=total_cost,
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='buy'
                )
                db.session.add(new_stock)
                db.session.commit()
                
                flash(f'You bought {quantity} {stock_name} stocks for {total_cost} successfully!', 'success')
        
        elif action == 'sell':
            # Check if the user has enough stocks to sell
            total_purchased_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='buy').scalar() or 0
            total_sold_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='sell').scalar() or 0
            available_quantity = total_purchased_quantity - total_sold_quantity
            
            if available_quantity <= 0:
                flash('Not enough stocks to sell', 'danger')
            elif quantity > available_quantity:
                flash('Quantity exceeds available stocks', 'danger')
            else:
                total_gain = current_price * quantity
                total_cost = current_price * quantity  # Correct the total cost

                current_user.wallet += total_gain
                db.session.commit()

                sold_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=-quantity,  # Negative quantity for sold stocks
                    total_cost=-total_cost,  # Negative total cost
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='sell'
                )
                db.session.add(sold_stock)
                db.session.commit()

                flash(f'You sold {quantity} {stock_name} stocks for {total_gain} successfully!', 'success')
                
        return redirect(url_for('airtel_page'))
    
    return render_template('airtle.html', current_price=current_price, stock_name=stock_name, wallet_amount=wallet_amount)






@app.route('/titan',methods=['GET','POST'])
@login_required
def titan_page():
    current_price = 3271
    stock_name = "Titan Company"
    wallet_amount = float(current_user.wallet)
    
       
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        action = request.form.get('action')
        
        if action == 'buy':
            total_cost = current_price * quantity
            
            if total_cost > wallet_amount:
                flash('Not enough funds in wallet to complete purchase', 'danger')
            else:
                current_user.wallet -= total_cost
                db.session.commit()
                
                new_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=quantity,
                    total_cost=total_cost,
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='buy'
                )
                db.session.add(new_stock)
                db.session.commit()
                
                flash(f'You bought {quantity} {stock_name} stocks for {total_cost} successfully!', 'success')
        
        elif action == 'sell':
            # Check if the user has enough stocks to sell
            total_purchased_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='buy').scalar() or 0
            total_sold_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='sell').scalar() or 0
            available_quantity = total_purchased_quantity - total_sold_quantity
            
            if available_quantity <= 0:
                flash('Not enough stocks to sell', 'danger')
            elif quantity > available_quantity:
                flash('Quantity exceeds available stocks', 'danger')
            else:
                total_gain = current_price * quantity
                total_cost = current_price * quantity  # Correct the total cost

                current_user.wallet += total_gain
                db.session.commit()

                sold_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=-quantity,  # Negative quantity for sold stocks
                    total_cost=-total_cost,  # Negative total cost
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='sell'
                )
                db.session.add(sold_stock)
                db.session.commit()

                flash(f'You sold {quantity} {stock_name} stocks for {total_gain} successfully!', 'success')
                
        return redirect(url_for('titan_page'))
    
    return render_template('titan.html', current_price=current_price, stock_name=stock_name, wallet_amount=wallet_amount)







@app.route('/zomato',methods=['GET','POST'])
@login_required
def zomato_page():
    current_price = 181
    stock_name = "zomato"
    wallet_amount = float(current_user.wallet)
    
       
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        action = request.form.get('action')
        
        if action == 'buy':
            total_cost = current_price * quantity
            
            if total_cost > wallet_amount:
                flash('Not enough funds in wallet to complete purchase', 'danger')
            else:
                current_user.wallet -= total_cost
                db.session.commit()
                
                new_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=quantity,
                    total_cost=total_cost,
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='buy'
                )
                db.session.add(new_stock)
                db.session.commit()
                
                flash(f'You bought {quantity} {stock_name} stocks for {total_cost} successfully!', 'success')
        
        elif action == 'sell':
            # Check if the user has enough stocks to sell
            total_purchased_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='buy').scalar() or 0
            total_sold_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='sell').scalar() or 0
            available_quantity = total_purchased_quantity - total_sold_quantity
            
            if available_quantity <= 0:
                flash('Not enough stocks to sell', 'danger')
            elif quantity > available_quantity:
                flash('Quantity exceeds available stocks', 'danger')
            else:
                total_gain = current_price * quantity
                total_cost = current_price * quantity  # Correct the total cost

                current_user.wallet += total_gain
                db.session.commit()

                sold_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=-quantity,  # Negative quantity for sold stocks
                    total_cost=-total_cost,  # Negative total cost
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='sell'
                )
                db.session.add(sold_stock)
                db.session.commit()

                flash(f'You sold {quantity} {stock_name} stocks for {total_gain} successfully!', 'success')
                
        return redirect(url_for('zomato_page'))
    
    return render_template('zomato.html', current_price=current_price, stock_name=stock_name, wallet_amount=wallet_amount)





@app.route('/yesbank',methods=['GET','POST'])
@login_required
def yesbank_page():
    current_price = 23
    stock_name = "Yes Bank"
    wallet_amount = float(current_user.wallet)
    
       
    if request.method == 'POST':
        quantity = int(request.form.get('quantity'))
        action = request.form.get('action')
        
        if action == 'buy':
            total_cost = current_price * quantity
            
            if total_cost > wallet_amount:
                flash('Not enough funds in wallet to complete purchase', 'danger')
            else:
                current_user.wallet -= total_cost
                db.session.commit()
                
                new_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=quantity,
                    total_cost=total_cost,
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='buy'
                )
                db.session.add(new_stock)
                db.session.commit()
                
                flash(f'You bought {quantity} {stock_name} stocks for {total_cost} successfully!', 'success')
        
        elif action == 'sell':
            # Check if the user has enough stocks to sell
            total_purchased_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='buy').scalar() or 0
            total_sold_quantity = db.session.query(db.func.sum(Portfolio.quantity)).filter_by(user_id=current_user.id, stock_name=stock_name, transaction_type='sell').scalar() or 0
            available_quantity = total_purchased_quantity - total_sold_quantity
            
            if available_quantity <= 0:
                flash('Not enough stocks to sell', 'danger')
            elif quantity > available_quantity:
                flash('Quantity exceeds available stocks', 'danger')
            else:
                total_gain = current_price * quantity
                total_cost = current_price * quantity  # Correct the total cost

                current_user.wallet += total_gain
                db.session.commit()

                sold_stock = Portfolio(
                    stock_name=stock_name,
                    current_price=current_price,
                    quantity=-quantity,  # Negative quantity for sold stocks
                    total_cost=-total_cost,  # Negative total cost
                    date_added=datetime.utcnow(),
                    user_id=current_user.id,
                    transaction_type='sell'
                )
                db.session.add(sold_stock)
                db.session.commit()

                flash(f'You sold {quantity} {stock_name} stocks for {total_gain} successfully!', 'success')
                
        return redirect(url_for('portfolio'))
    
    return render_template('yesbank.html', current_price=current_price, stock_name=stock_name, wallet_amount=wallet_amount)






stock_analysis_routes = {
    'Suzlon Energy': 'suzlon_page',
    'MRF Ltd.': 'mrf_page',
    'Infosys':'infosys_page',
    'TATA MOTORS.':'tata_motors_page',
    'RELIANCE POWER':'rpower_page',
    'Adani green':'adani_green_page',
    'Bharathi airtel':'airtel_page',
    'Titan Company':'titan_page',
    'zomato':'zomato_page',
    'Yes Bank':'yesbank_page'
    # Add more mappings as needed
}


@app.route('/portfolio')
@login_required
def portfolio():
    portfolio_items = Portfolio.query.filter_by(user_id=current_user.id).all()
    portfolio_data = {}

    for item in portfolio_items:
        if item.stock_name not in portfolio_data:
            portfolio_data[item.stock_name] = {
                'stock_name': item.stock_name,
                'current_price': item.current_price,
                'purchased_quantity': 0,
                'sold_quantity': 0,
                'current_quantity': 0,
                'total_cost': 0,
                'date_added': item.date_added
            }

        if item.transaction_type == 'buy':
            portfolio_data[item.stock_name]['purchased_quantity'] += item.quantity
            portfolio_data[item.stock_name]['total_cost'] += item.total_cost
        elif item.transaction_type == 'sell':
            portfolio_data[item.stock_name]['sold_quantity'] += abs(item.quantity)
            portfolio_data[item.stock_name]['total_cost'] -= abs(item.total_cost)

        portfolio_data[item.stock_name]['current_quantity'] = portfolio_data[item.stock_name]['purchased_quantity'] - portfolio_data[item.stock_name]['sold_quantity']

    return render_template('portfolio.html', portfolio_items=portfolio_data.values(), stock_analysis_routes=stock_analysis_routes)




