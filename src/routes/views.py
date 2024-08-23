from flask import Blueprint, render_template

view_bp = Blueprint('views', __name__)

@view_bp.get("/")
def index():
    return render_template('index.html')
