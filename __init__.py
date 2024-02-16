from flask import Blueprint
app_routes = Blueprint('app_routes', __name__)
from . import routes
