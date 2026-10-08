from flask import Blueprint, current_app, jsonify

from database.db import get_dashboard_metrics

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/dashboard')
def dashboard_data():
    """Expose lightweight aggregates for automatic Chart.js updates."""
    metrics = get_dashboard_metrics(current_app.config['DATABASE_PATH'])
    metrics['recent_assessments'] = [
        {
            'id': assessment.id,
            'course': assessment.course,
            'risk_level': assessment.risk_level,
            'total_score': assessment.total_score,
        }
        for assessment in metrics['recent_assessments']
    ]
    return jsonify(metrics)
