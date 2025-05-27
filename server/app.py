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
        """Get public key for a user"""
        try:
            public_key = key_manager.get_public_key_pem(user_id)
            
            if public_key:
                return jsonify({
                    'status': 'success',
                    'user_id': user_id,
                    'public_key': public_key
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': ERROR_MESSAGES['KEY_NOT_FOUND']
                }), 404
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """Handle file upload"""
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        user_id = request.form.get('user_id')
        
        if not user_id:
            return jsonify({
                'status': 'error',
                'message': 'User ID is required'
            }), 400
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No file selected'
            }), 400
        
        if not file_handler.allowed_file(file.filename):
            return jsonify({
                'status': 'error',
                'message': ERROR_MESSAGES['INVALID_FILE']
            }), 400
        
        try:
            # Read file content
            file_data = file.read()
            
            # Validate file size
            is_valid, message = file_handler.validate_file_size(len(file_data))
            if not is_valid:
                return jsonify({
                    'status': 'error',
                    'message': message
                }), 400
            
            # Save file
            file_id, file_path, file_size = file_handler.save_uploaded_file(
                file_data, file.filename, user_id
            )
            
            return jsonify({
                'status': 'success',
                'message': 'File uploaded successfully',
                'file_id': file_id,
                'file_size': file_size,
                'file_hash': crypto_utils.hash_file(file_data)
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/api/encrypt_and_send', methods=['POST'])
    def encrypt_and_send():
        """Encrypt file and prepare for sending"""
        data = request.json
        
        file_id = data.get('file_id')
        sender_id = data.get('sender_id')
        recipient_id = data.get('recipient_id')
        file_path = data.get('file_path')
        
        if not all([file_id, sender_id, recipient_id, file_path]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400
        
        try:
            # Load file
            file_data = file_handler.get_file_content(file_path)
            if not file_data:
                return jsonify({
                    'status': 'error',
                    'message': 'File not found'
                }), 404
            
            # Prepare for transfer
            transfer_package = secure_transfer.prepare_file_for_transfer(
                file_data,
                os.path.basename(file_path),
                sender_id,
                recipient_id
            )
            
            return jsonify({
                'status': 'success',
                'message': 'File encrypted successfully',
                'transfer_package': transfer_package
            })
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/api/decrypt_file', methods=['POST'])
    def decrypt_file():
        """Decrypt received file"""
        data = request.json
        transfer_package = data.get('transfer_package')
        
        if not transfer_package:
            return jsonify({
                'status': 'error',
                'message': 'No transfer package provided'
            }), 400
        
        try:
            # Process received file
            file_data, file_name, is_valid, message = secure_transfer.receive_and_process_file(
                transfer_package
            )
            
            # Save decrypted file
            if file_data:
                file_path = file_handler.save_decrypted_file(
                    file_data,
                    file_name,
                    transfer_package['recipient_id'],
                    transfer_package.get('transfer_id', 'temp')
                )
                
                return jsonify({
                    'status': 'success',
                    'message': message,
                    'is_valid': is_valid,
                    'file_path': file_path,
                    'file_size': len(file_data)
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to decrypt file'
                }), 500
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/api/download/<path:file_path>')
    def download_file(file_path):
        """Download decrypted file"""
        try:
            # Security check - ensure file is in allowed directory
            full_path = os.path.abspath(file_path)
            upload_dir = os.path.abspath(app.config['UPLOAD_FOLDER'])
            
            if not full_path.startswith(upload_dir):
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid file path'
                }), 403
            
            if os.path.exists(full_path):
                return send_file(full_path, as_attachment=True)
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'File not found'
                }), 404
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        """Handle file too large error"""
        return jsonify({
            'status': 'error',
            'message': ERROR_MESSAGES['FILE_TOO_LARGE']
        }), 413
    
    @app.errorhandler(404)
    def handle_not_found(e):
        """Handle 404 errors"""
        return jsonify({
            'status': 'error',
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_server_error(e):
        """Handle server errors"""
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500
    
    return app, socketio