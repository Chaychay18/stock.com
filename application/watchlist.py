from application import app
from flask_login import login_user, current_user, login_required
from application.models import watchlist
from flask import render_template, request, jsonify, redirect, url_for, send_from_directory,flash
from application import db





stock_analysis_routes = {
    'Suzlon Energy': 'suzlon_page',
    'MRF Ltd.': 'mrf_page',
    'Infosys':'infosys_page',
    'TATA MOTORS.':'tata_motors_page',
    'TATA MOTORS':'tata_motors_page',
    'RELIANCE POWER':'rpower_page',
    'Adani green':'adani_green_page',
    'Bharathi airtel':'airtel_page',
    'Titan Company':'titan_page',
    'zomato':'zomato_page',
    'Yes Bank':'yesbank_page'

    # Add more mappings as needed
}


@app.route('/add_to_watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    stock_name = request.form.get('stock_name')
    current_price = request.form.get('current_price')
    
    # Check if the stock is already in the watchlist
    existing_entry = watchlist.query.filter_by(stock_name=stock_name, user_id=current_user.id).first()
    if existing_entry:
        flash('This stock is already in your watchlist.', 'warning')
    else:
        new_watchlist_item = watchlist(
            stock_name=stock_name,
            current_price=current_price,
            user_id=current_user.id
        )
        db.session.add(new_watchlist_item)
        db.session.commit()
        flash('Stock added to watchlist successfully!', 'success')
    
    return redirect(url_for('stocks'))

@app.route('/watchlist')
@login_required 
def watchlist_page():
    user_id = current_user.id 
    watchlist_items = watchlist.query.filter_by(user_id=user_id).all()
    return render_template('watchlist.html',watchlist_items=watchlist_items,stock_analysis_routes=stock_analysis_routes)