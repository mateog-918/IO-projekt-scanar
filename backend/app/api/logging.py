"""
API endpoints for accessing event logs
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
    Get all logs with optional pagination
    
    Query parameters:
        limit: Number of results per page (default: 100)
        offset: Number of results to skip (default: 0)
        
    Returns:
        JSON with logs and pagination info
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
    Get logs filtered by event type
    
    URL parameters:
        event_type: Event type filter (INVALID_QR, FACE_MISMATCH, VERIFICATION_SUCCESS, etc.)
        
    Query parameters:
        limit: Number of results per page (default: 100)
        offset: Number of results to skip (default: 0)
        
    Returns:
        JSON with filtered logs and pagination info
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
    Get logs for a specific employee
    
    URL parameters:
        employee_id: Employee ID
        
    Query parameters:
        limit: Number of results per page (default: 100)
        offset: Number of results to skip (default: 0)
        
    Returns:
        JSON with employee logs and pagination info
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
    Get logs within a date range
    
    Query parameters:
        start_date: Start date (ISO format: 2024-01-01T00:00:00)
        end_date: End date (ISO format: 2024-01-31T23:59:59)
        limit: Number of results per page (default: 100)
        offset: Number of results to skip (default: 0)
        
    Returns:
        JSON with filtered logs and pagination info
    """
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': 'start_date and end_date parameters are required (ISO format)'
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
    Get event statistics (count by event type)
    
    Returns:
        JSON with event type statistics
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
    Get the image associated with a log entry
    
    URL parameters:
        log_id: Event log ID
        
    Returns:
        Image file or error JSON
    """
    try:
        from app.models.event_log import EventLog
        
        log = EventLog.query.get(log_id)
        
        if not log:
            return jsonify({'success': False, 'error': 'Log entry not found'}), 404
        
        if not log.image_path:
            return jsonify({'success': False, 'error': 'No image associated with this log'}), 404
        
        # Construct full path
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
    Get all available event types
    
    Returns:
        JSON with list of available event types
    """
    try:
        event_types = [et.value for et in EventType]
        
        return jsonify({
            'success': True,
            'event_types': event_types
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
