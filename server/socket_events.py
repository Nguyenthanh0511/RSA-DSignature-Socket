# server/socket_events.py
"""
WebSocket event handlers
"""

from flask_socketio import emit, join_room, leave_room
from flask import request
import uuid
import json
from datetime import datetime
from shared.constants import SOCKET_EVENTS, STATUS, ERROR_MESSAGES
from shared.models import db, User, FileTransfer, PublicKeyRegistry


class SocketEventHandlers:
    """Handles WebSocket events"""
    
    def __init__(self, socketio, key_manager, file_handler, crypto_utils):
        self.socketio = socketio
        self.key_manager = key_manager
        self.file_handler = file_handler
        self.crypto_utils = crypto_utils
        self.active_connections = {}
        
        # Register event handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Register all socket event handlers"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            client_id = request.sid
            self.active_connections[client_id] = {
                'connected_at': datetime.now(),
                'user_id': None
            }
            
            emit('connected', {
                'status': STATUS['SUCCESS'],
                'client_id': client_id,
                'message': 'Connected to server'
            })
            
            print(f"Client connected: {client_id}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            client_id = request.sid
            if client_id in self.active_connections:
                del self.active_connections[client_id]
            
            print(f"Client disconnected: {client_id}")
        
        @self.socketio.on('register_user')
        def handle_register_user(data):
            """Register user and generate keys if needed"""
            client_id = request.sid
            user_id = data.get('user_id')
            username = data.get('username', user_id)
            
            if not user_id:
                emit('error', {
                    'message': 'User ID is required'
                })
                return
            
            # Update connection info
            self.active_connections[client_id]['user_id'] = user_id
            
            # Check if user exists
            user = User.query.filter_by(user_id=user_id).first()
            
            if not user:
                # Create new user
                user = User(user_id=user_id, username=username)
                
                # Generate key pair
                private_key, public_key = self.key_manager.generate_key_pair()
                
                # Save keys
                self.key_manager.save_key_pair(user_id, private_key, public_key)
                
                # Save public key to registry
                public_key_str = public_key.decode('utf-8')
                user.public_key = public_key_str
                
                # Create registry entry
                registry = PublicKeyRegistry(
                    user_id=user_id,
                    public_key=public_key_str,
                    fingerprint=self.crypto_utils.hash_file(public_key)[:16]
                )
                
                db.session.add(user)
                db.session.add(registry)
                db.session.commit()
                
                emit('keys_generated', {
                    'status': STATUS['SUCCESS'],
                    'user_id': user_id,
                    'public_key': public_key_str,
                    'message': 'Keys generated successfully'
                })
            else:
                # Update last active
                user.last_active = datetime.utcnow()
                db.session.commit()
                
                emit('user_registered', {
                    'status': STATUS['SUCCESS'],
                    'user_id': user_id,
                    'has_keys': bool(user.public_key),
                    'message': 'User registered successfully'
                })
            
            # Join user room
            join_room(user_id)
        
        @self.socketio.on('request_public_key')
        def handle_request_public_key(data):
            """Handle public key request"""
            requested_user_id = data.get('user_id')
            
            if not requested_user_id:
                emit('error', {
                    'message': 'User ID is required'
                })
                return
            
            # Get public key from registry
            registry = PublicKeyRegistry.query.filter_by(
                user_id=requested_user_id
            ).first()
            
            if registry:
                emit('public_key_response', {
                    'status': STATUS['SUCCESS'],
                    'user_id': requested_user_id,
                    'public_key': registry.public_key,
                    'fingerprint': registry.fingerprint
                })
            else:
                emit('public_key_response', {
                    'status': STATUS['ERROR'],
                    'message': ERROR_MESSAGES['KEY_NOT_FOUND']
                })
        
        @self.socketio.on('send_file')
        def handle_send_file(data):
            """Handle file sending"""
            client_id = request.sid
            sender_id = self.active_connections[client_id].get('user_id')
            
            if not sender_id:
                emit('error', {
                    'message': 'User not registered'
                })
                return
            
            # Extract data
            recipient_id = data.get('recipient_id')
            encrypted_package = data.get('encrypted_package')
            
            if not recipient_id or not encrypted_package:
                emit('error', {
                    'message': 'Missing required data'
                })
                return
            
            # Generate transfer ID
            transfer_id = str(uuid.uuid4())
            
            # Save encrypted file
            encrypted_path = self.file_handler.save_encrypted_file(
                encrypted_package, transfer_id
            )
            
            # Create transfer record
            transfer = FileTransfer(
                transfer_id=transfer_id,
                sender_id=sender_id,
                recipient_id=recipient_id,
                file_name=encrypted_package.get('file_name', 'unknown'),
                file_size=len(json.dumps(encrypted_package)),
                file_hash=encrypted_package.get('file_hash', ''),
                encrypted_file_path=encrypted_path,
                status=STATUS['PENDING']
            )
            
            db.session.add(transfer)
            db.session.commit()
            
            # Notify sender
            emit('file_sent', {
                'status': STATUS['SUCCESS'],
                'transfer_id': transfer_id,
                'message': 'File sent successfully'
            })
            
            # Notify recipient if online
            self.socketio.emit('file_received', {
                'transfer_id': transfer_id,
                'sender_id': sender_id,
                'file_name': encrypted_package.get('file_name'),
                'timestamp': datetime.now().isoformat()
            }, room=recipient_id)
        
        @self.socketio.on('download_file')
        def handle_download_file(data):
            """Handle file download request"""
            client_id = request.sid
            user_id = self.active_connections[client_id].get('user_id')
            transfer_id = data.get('transfer_id')
            
            if not user_id or not transfer_id:
                emit('error', {
                    'message': 'Invalid request'
                })
                return
            
            # Get transfer record
            transfer = FileTransfer.query.filter_by(
                transfer_id=transfer_id,
                recipient_id=user_id
            ).first()
            
            if not transfer:
                emit('error', {
                    'message': 'Transfer not found'
                })
                return
            
            # Load encrypted package
            encrypted_package = self.file_handler.load_encrypted_file(transfer_id)
            
            if not encrypted_package:
                emit('error', {
                    'message': 'Encrypted file not found'
                })
                return
            
            # Send encrypted package to recipient
            emit('file_download_response', {
                'status': STATUS['SUCCESS'],
                'transfer_id': transfer_id,
                'encrypted_package': encrypted_package,
                'sender_id': transfer.sender_id
            })
        
        @self.socketio.on('report_decryption_result')
        def handle_decryption_result(data):
            """Handle decryption result report"""
            transfer_id = data.get('transfer_id')
            success = data.get('success', False)
            signature_valid = data.get('signature_valid', False)
            integrity_valid = data.get('integrity_valid', False)
            error_message = data.get('error_message')
            
            # Update transfer record
            transfer = FileTransfer.query.filter_by(
                transfer_id=transfer_id
            ).first()
            
            if transfer:
                transfer.status = STATUS['SUCCESS'] if success else STATUS['FAILED']
                transfer.signature_valid = signature_valid
                transfer.integrity_valid = integrity_valid
                transfer.error_message = error_message
                transfer.completed_at = datetime.utcnow()
                
                db.session.commit()
                
                # Notify sender
                self.socketio.emit('transfer_completed', {
                    'transfer_id': transfer_id,
                    'status': transfer.status,
                    'signature_valid': signature_valid,
                    'integrity_valid': integrity_valid
                }, room=transfer.sender_id)
        
        @self.socketio.on('get_transfer_history')
        def handle_get_transfer_history(data):
            """Get transfer history for user"""
            client_id = request.sid
            user_id = self.active_connections[client_id].get('user_id')
            
            if not user_id:
                emit('error', {
                    'message': 'User not registered'
                })
                return
            
            # Get sent transfers
            sent_transfers = FileTransfer.query.filter_by(
                sender_id=user_id
            ).order_by(FileTransfer.created_at.desc()).limit(50).all()
            
            # Get received transfers
            received_transfers = FileTransfer.query.filter_by(
                recipient_id=user_id
            ).order_by(FileTransfer.created_at.desc()).limit(50).all()
            
            emit('transfer_history_response', {
                'sent': [t.to_dict() for t in sent_transfers],
                'received': [t.to_dict() for t in received_transfers]
            })
        
        @self.socketio.on('get_online_users')
        def handle_get_online_users():
            """Get list of online users"""
            online_users = []
            
            for conn_id, conn_info in self.active_connections.items():
                if conn_info['user_id']:
                    user = User.query.filter_by(
                        user_id=conn_info['user_id']
                    ).first()
                    
                    if user:
                        online_users.append({
                            'user_id': user.user_id,
                            'username': user.username,
                            'has_public_key': bool(user.public_key)
                        })
            
            emit('online_users_response', {
                'users': online_users
            })