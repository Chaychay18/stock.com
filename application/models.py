from application import app, db
from application import bcrypt
from flask_login import UserMixin
from application import login_manager
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
     return Users.query.get(int(user_id))

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False, unique=True)
    email_address = db.Column(db.String(50), nullable=False, unique=True)
    pan_number = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(60), nullable=False)
    wallet = db.Column(db.Float, default=2000.0)  

    portfolios = db.relationship('Portfolio', backref='owner', lazy=True)
    
    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)
 

    app.app_context().push()

    def __repr__(self):
        return f'<Users {self.first_name} {self.last_name} {self.phone_number} {self.email_address} {self.pan_number}>'

class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(150), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    total_cost = db.Column(db.Float, nullable=False, default=0.0)
    transaction_type = db.Column(db.String(10), nullable=False, default='buy')


    app.app_context().push()

    def __repr__(self):
        return f'<Portfolio {self.stock_name} {self.current_price} {self.date_added} {self.quantity} {self.total_cost} {self.transaction_type}>'
    


class watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(150), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


    app.app_context().push()

    def __repr__(self):
        return f'<Portfolio {self.stock_name} {self.current_price}>'