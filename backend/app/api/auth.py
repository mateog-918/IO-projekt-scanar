from flask import Blueprint, request, jsonify, session
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Hardcoded admin credentials
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'admin123'
}


def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({'success': False, 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Admin login endpoint
    Expects JSON: {"username": "admin", "password": "admin123"}
    Returns: {"success": true/false, "message": "...", "user": {...}}
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'}), 400
        
        # Check credentials
        if username == ADMIN_CREDENTIALS['username'] and password == ADMIN_CREDENTIALS['password']:
            session['logged_in'] = True
            session['username'] = username
            return jsonify({
                'success': True, 
                'message': 'Login successful',
                'user': {'username': username}
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint - clears session"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@auth_bp.route('/status', methods=['GET'])
def status():
    """Check if user is logged in"""
    if session.get('logged_in'):
        return jsonify({
            'logged_in': True,
            'username': session.get('username')
        }), 200
    else:
        return jsonify({'logged_in': False}), 200
