from datetime import date
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# app sqldatabase config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock.db'
db = SQLAlchemy(app)

# sql database implementation
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False)

class DailyDispense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dispense_date = db.Column(db.Date, nullable=False, unique=True)
    count = db.Column(db.Integer, nullable=False)

# initialise database
@app.before_first_request
def create_tables():
    db.create_all()
    if Stock.query.count() == 0:
        initial_stock = Stock(count=0)
        db.session.add(initial_stock)
        db.session.commit()

@app.route('/get_stock', methods=['GET'])
def get_stock():
    stock = Stock.query.first()
    return jsonify({'stock': stock.count})

@app.route('/add_stock', methods=['POST'])
def add_stock():
    try:
        amount = request.args.get('amount')
        if amount is None:
            return jsonify({'error': 'Amount parameter is missing'}), 400

        amount = int(amount)
        stock = Stock.query.first()
        stock.count += amount
        db.session.commit()
        return jsonify({'stock': stock.count}), 200
    except ValueError:
        return jsonify({'error': 'Invalid amount parameter'}), 400

@app.route('/dispense', methods=['POST'])
def dispense():
    dispense_count = request.json.get('count', 1)
    stock = Stock.query.first()
    
    if stock.count >= dispense_count:
        stock.count -= dispense_count
        
        # Get today's date
        today = date.today()
        daily_dispense = DailyDispense.query.filter_by(dispense_date=today).first()
        
        if daily_dispense:
            daily_dispense.count += dispense_count
        else:
            daily_dispense = DailyDispense(dispense_date=today, count=dispense_count)
            db.session.add(daily_dispense)
        
        db.session.commit()
        return jsonify({'stock': stock.count}), 200
    else:
        return jsonify({'error': 'Insufficient stock'}), 400

@app.route('/daily_dispense', methods=['GET'])
def daily_dispense():
    dispenses = DailyDispense.query.all()
    return jsonify([{'date': d.dispense_date.isoformat(), 'count': d.count} for d in dispenses])

if __name__ == '__main__':
    app.run(host='https://autovendcapsuletester.pythonanywhere.com/', port=5000)
