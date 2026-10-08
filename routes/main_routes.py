from flask import Blueprint, current_app, render_template

from database.db import get_dashboard_metrics

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def dashboard():
    metrics = get_dashboard_metrics(current_app.config['DATABASE_PATH'])
    return render_template('dashboard.html', metrics=metrics)


@main_bp.route('/sobre')
def about():
    return render_template('about.html')
