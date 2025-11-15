"""
Health Check Routes
"""
from flask import Blueprint, jsonify
from datetime import datetime

bp = Blueprint('health', __name__, url_prefix='/api')

@bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'Fingerprint Attendance System API is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
