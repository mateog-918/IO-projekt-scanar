"""
Logging service for handling event logging and retrieval
"""
import os
import base64
from datetime import datetime, timezone
from app.models.event_log import EventLog, EventType
from app.models.employee import db
from werkzeug.utils import secure_filename


class LoggingService:
    """Service for logging and retrieving verification events"""

    # Configure image storage
    IMAGE_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'logs')
    
    @staticmethod
    def ensure_log_dir_exists():
        """Ensure the log image storage directory exists"""
        if not os.path.exists(LoggingService.IMAGE_STORAGE_DIR):
            os.makedirs(LoggingService.IMAGE_STORAGE_DIR, exist_ok=True)

    @staticmethod
    def save_image(image_bytes, event_type, employee_id=None):
        """
        Save image bytes to disk and return the file path
        
        Args:
            image_bytes: Binary image data
            event_type: Type of event (for organization)
            employee_id: Optional employee ID for organization
            
        Returns:
            str: Relative file path to saved image or None if save failed
        """
        try:
            LoggingService.ensure_log_dir_exists()
            
            # Create subdirectory by event type
            event_dir = os.path.join(LoggingService.IMAGE_STORAGE_DIR, event_type)
            os.makedirs(event_dir, exist_ok=True)
            
            # Generate filename with timestamp
            # use UTC timestamp for filenames
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')[:-3]
            filename = f"{event_type}_{employee_id}_{timestamp}.png" if employee_id else f"{event_type}_{timestamp}.png"
            filename = secure_filename(filename)
            
            file_path = os.path.join(event_dir, filename)
            
            # Write image data to file
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            
            # Return relative path for storage in database
            relative_path = os.path.relpath(file_path, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            return relative_path
        except Exception as e:
            print(f"Error saving image: {e}")
            return None

    @staticmethod
    def log_event(event_type, employee_id=None, qr_code_hash=None, image_bytes=None, message=None):
        """
        Log a verification event to the database
        
        Args:
            event_type: EventType enum or string (e.g., 'INVALID_QR', 'FACE_MISMATCH', 'VERIFICATION_SUCCESS')
            employee_id: ID of the employee (may be None for invalid QR)
            qr_code_hash: The QR code hash that was scanned
            image_bytes: Binary image data from camera (optional)
            message: Additional message/context for the event
            
        Returns:
            EventLog: The created event log entry
        """
        try:
            # Convert EventType enum to string if needed
            if isinstance(event_type, EventType):
                event_type_str = event_type.value
            else:
                event_type_str = str(event_type)
            
            # Get employee name snapshot (immutable log record)
            employee_name = None
            if employee_id:
                from app.models.employee import Employee
                emp = Employee.query.get(employee_id)
                if emp:
                    employee_name = emp.name
            
            # Save image if provided
            image_path = None
            if image_bytes:
                image_path = LoggingService.save_image(image_bytes, event_type_str, employee_id)
            
            # Create event log entry with snapshot of employee name
            event_log = EventLog(
                event_type=event_type_str,
                employee_id=employee_id,
                employee_name=employee_name,
                qr_code_hash=qr_code_hash,
                image_path=image_path,
                message=message,
                timestamp=datetime.now(timezone.utc)
            )
            
            db.session.add(event_log)
            db.session.commit()
            
            return event_log
        except Exception as e:
            print(f"Error logging event: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def get_logs_by_type(event_type, limit=100, offset=0):
        """
        Retrieve logs filtered by event type
        
        Args:
            event_type: EventType to filter by (string or enum)
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            tuple: (list of EventLog entries, total count)
        """
        try:
            if isinstance(event_type, EventType):
                event_type_str = event_type.value
            else:
                event_type_str = str(event_type)
            
            query = EventLog.query.filter_by(event_type=event_type_str).order_by(EventLog.timestamp.desc())
            total = query.count()
            logs = query.limit(limit).offset(offset).all()
            
            return logs, total
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return [], 0

    @staticmethod
    def get_all_logs(limit=100, offset=0):
        """
        Retrieve all logs with optional pagination
        
        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            tuple: (list of EventLog entries, total count)
        """
        try:
            query = EventLog.query.order_by(EventLog.timestamp.desc())
            total = query.count()
            logs = query.limit(limit).offset(offset).all()
            
            return logs, total
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return [], 0

    @staticmethod
    def get_logs_by_employee(employee_id, limit=100, offset=0):
        """
        Retrieve logs for a specific employee
        
        Args:
            employee_id: Employee ID to filter by
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            tuple: (list of EventLog entries, total count)
        """
        try:
            query = EventLog.query.filter_by(employee_id=employee_id).order_by(EventLog.timestamp.desc())
            total = query.count()
            logs = query.limit(limit).offset(offset).all()
            
            return logs, total
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return [], 0

    @staticmethod
    def get_logs_date_range(start_date, end_date, limit=100, offset=0):
        """
        Retrieve logs within a date range
        
        Args:
            start_date: Start datetime
            end_date: End datetime
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            tuple: (list of EventLog entries, total count)
        """
        try:
            query = EventLog.query.filter(
                EventLog.timestamp >= start_date,
                EventLog.timestamp <= end_date
            ).order_by(EventLog.timestamp.desc())
            total = query.count()
            logs = query.limit(limit).offset(offset).all()
            
            return logs, total
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return [], 0

    @staticmethod
    def get_event_statistics():
        """
        Get statistics about events
        
        Returns:
            dict: Event type counts and total
        """
        try:
            stats = {}
            all_events = EventLog.query.all()
            total = len(all_events)
            
            for event in all_events:
                event_type = event.event_type
                stats[event_type] = stats.get(event_type, 0) + 1
            
            stats['total'] = total
            return stats
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {'total': 0}
