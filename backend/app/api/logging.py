"""
Logging API Module
------------------
This module provides endpoints for retrieving and filtering event logs, 
generating statistics, and accessing captured verification images.
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import os
from app.services.logging_service import LoggingService
from app.models.event_log import EventType

logging_bp = Blueprint('logging', __name__, url_prefix='/api/logs')


@logging_bp.route('/', methods=['GET'])
def get_all_logs():
    """
    Retrieves all logs with optional pagination.
    
    **Query Parameters:**
        * **limit** (int): Number of results per page (default: 100).
        * **offset** (int): Number of results to skip (default: 0).
        
    **Returns:**

    .. code-block:: json

        {
            "success": true,
            "total": 500,
            "limit": 100,
            "offset": 0,
            "logs": []
        }
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        logs, total = LoggingService.get_all_logs(limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'total': total,
            'limit': limit,
            'offset': offset,
            'logs': [log.to_dict() for log in logs]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@logging_bp.route('/type/<event_type>', methods=['GET'])
def get_logs_by_event_type(event_type):
    """
    Retrieves logs filtered by a specific event type.
    
    **URL Parameters:**
        * **event_type** (str): The type filter (e.g., 'INVALID_QR').
        
    **Query Parameters:**
        * **limit** (int): Results per page.
        * **offset** (int): Results skip count.
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        logs, total = LoggingService.get_logs_by_type(event_type, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'event_type': event_type,
            'total': total,
            'limit': limit,
            'offset': offset,
            'logs': [log.to_dict() for log in logs]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@logging_bp.route('/employee/<int:employee_id>', methods=['GET'])
def get_logs_by_employee(employee_id):
    """
    Retrieves all logs associated with a specific employee.
    
    **URL Parameters:**
        * **employee_id** (int): The ID of the employee.
    """
    try:
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        logs, total = LoggingService.get_logs_by_employee(employee_id, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'employee_id': employee_id,
            'total': total,
            'limit': limit,
            'offset': offset,
            'logs': [log.to_dict() for log in logs]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@logging_bp.route('/date-range', methods=['GET'])
def get_logs_date_range():
    """
    Retrieves logs within a specified date and time range.
    
    **Query Parameters:**
        * **start_date** (str): Start date in ISO format.
        * **end_date** (str): End date in ISO format.
    """
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': 'start_date and end_date parameters are required'
            }), 400
        
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        logs, total = LoggingService.get_logs_date_range(start_date, end_date, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'total': total,
            'limit': limit,
            'offset': offset,
            'logs': [log.to_dict() for log in logs]
        }), 200
    except ValueError as e:
        return jsonify({'success': False, 'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@logging_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Retrieves aggregated statistics of event counts grouped by type.
    
    **Returns:**

    .. code-block:: json

        {
            "success": true,
            "statistics": {
                "VERIFICATION_SUCCESS": 150,
                "FACE_MISMATCH": 12
            }
        }
    """
    try:
        stats = LoggingService.get_event_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@logging_bp.route('/image/<log_id>', methods=['GET'])
def get_log_image(log_id):
    """
    Serves the physical image file associated with a specific log entry.
    """
    try:
        from app.models.event_log import EventLog
        
        log = EventLog.query.get(log_id)
        
        if not log:
            return jsonify({'success': False, 'error': 'Log entry not found'}), 404
        
        if not log.image_path:
            return jsonify({'success': False, 'error': 'No image associated'}), 404
        
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        full_path = os.path.join(base_path, log.image_path)
        
        if not os.path.exists(full_path):
            return jsonify({'success': False, 'error': 'Image file not found'}), 404
        
        return send_file(full_path, mimetype='image/png')
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@logging_bp.route('/event-types', methods=['GET'])
def get_event_types():
    """
    Retrieves a list of all possible event types used by the system.
    """
    try:
        event_types = [et.value for et in EventType]
        return jsonify({'success': True, 'event_types': event_types}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500