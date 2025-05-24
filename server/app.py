# server/app.py
"""
Main Flask application
"""

import os
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO
from flask_cors import CORS
from werkzeug.exceptions import RequestEntityTooLarge

from server.config import config
from server.key_manager import KeyManager
from server.crypto_utils import CryptoUtils, SecureFileTransfer
from server.file_handler import FileHandler
from server.socket_events import SocketEventHandlers
from shared.models import db
from shared.constants import ERROR_MESSAGES


def create_app(config_name='default'):
    """Create and configure Flask app"""
    
    app = Flask(__name__, 
                template_folder='../client/templates',
                static_folder='../client/static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    socketio = SocketIO(app, cors_allowed_origins="*")
    
    # Initialize services
    key_manager = KeyManager(app.config['SERVER_KEYS_DIR'])
    file_handler = FileHandler(app.config['UPLOAD_FOLDER'])
    crypto_utils = CryptoUtils()
    secure_transfer = SecureFileTransfer(key_manager)
    
    # Initialize socket handlers
    socket_handlers = SocketEventHandlers(
        socketio, key_manager, file_handler, crypto_utils
    )
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Routes
    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')
    
    @app.route('/sender')
    def sender_page():
        """Sender interface"""
        return render_template('sender.html')
    
    @app.route('/receiver')
    def receiver_page():
        """Receiver interface"""
        return render_template('receiver.html')
    
    @app.route('/api/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'message': 'Server is running'
        })
    
    @app.route('/api/generate_keys', methods=['POST'])
    def generate_keys():
        """Generate new key pair"""
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'User ID is required'
            }), 400
        
        try:
            # Generate keys
            private_key, public_key = key_manager.generate_key_pair()
            
            # Save keys
            paths = key_manager.save_key_pair(user_id, private_key, public_key)
            
            return jsonify({
                'status': 'success',
                'message': 'Keys generated successfully',
                'public_key': public_key.decode('utf-8')
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/api/public_key/<user_id>')
    def get_public_key(user_id):