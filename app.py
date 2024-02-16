# app.py
from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from routes import app_routes
from models import Base
from sqlalchemy import create_engine
from config import CONFIG

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = CONFIG.JWT_SECRET_KEY
jwt = JWTManager(app)

app.register_blueprint(app_routes)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loginpage')
def loginpage():
    return render_template('login.html')

@app.route('/registerpage')
def registerpage():
    return render_template('register.html')

@app.route('/taskspage')
def taskspage():
    return render_template('tasks.html')


DATABASE_URL = CONFIG.SQLALCHEMY_DATABASE_URI
engine = create_engine(DATABASE_URL)

Base.metadata.create_all(engine)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int("8043"))