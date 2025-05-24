# shared/models.py
"""
Database models for the application
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """User model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    public_key = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sent_transfers = db.relationship('FileTransfer', foreign_keys='FileTransfer.sender_id', 
                                   backref='sender', lazy='dynamic')
    received_transfers = db.relationship('FileTransfer', foreign_keys='FileTransfer.recipient_id',
                                       backref='recipient', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'has_public_key': bool(self.public_key),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }


class FileTransfer(db.Model):
    """File transfer history"""
    __tablename__ = 'file_transfers'
    
    id = db.Column(db.Integer, primary_key=True)
    transfer_id = db.Column(db.String(100), unique=True, nullable=False)
    sender_id = db.Column(db.String(100), db.ForeignKey('users.user_id'), nullable=False)
    recipient_id = db.Column(db.String(100), db.ForeignKey('users.user_id'), nullable=False)
    
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_hash = db.Column(db.String(64), nullable=False)
    
    encrypted_file_path = db.Column(db.String(500), nullable=True)
    
    status = db.Column(db.String(50), default='pending')
    signature_valid = db.Column(db.Boolean, default=None)
    integrity_valid = db.Column(db.Boolean, default=None)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    error_message = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'transfer_id': self.transfer_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_hash': self.file_hash,
            'status': self.status,
            'signature_valid': self.signature_valid,
            'integrity_valid': self.integrity_valid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }


class PublicKeyRegistry(db.Model):
    """Public key registry for all users"""
    __tablename__ = 'public_key_registry'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    public_key = db.Column(db.Text, nullable=False)
    fingerprint = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'public_key': self.public_key,
            'fingerprint': self.fingerprint,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }