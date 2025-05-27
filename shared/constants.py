# shared/constants.py
"""
Constants used throughout the application
"""

# RSA Key Configuration
RSA_KEY_SIZE = 2048
RSA_PUBLIC_EXPONENT = 65537

# File Configuration
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for large files
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
    'doc', 'docx', 'json', 'xml', 'csv'
}

# Cryptography
HASH_ALGORITHM = 'SHA-256'
ENCODING = 'utf-8'

# WebSocket Events
SOCKET_EVENTS = {
    'connect': 'connect',
    'disconnect': 'disconnect',
    'request_public_key': 'request_public_key',
    'send_public_key': 'send_public_key',
    'send_file': 'send_file',
    'receive_file': 'receive_file',
    'file_received': 'file_received',
    'verify_signature': 'verify_signature',
    'signature_result': 'signature_result',
    'error': 'error',
    'file_transfer_progress': 'file_transfer_progress'
}

# Status Codes
STATUS = {
    'SUCCESS': 'success',
    'ERROR': 'error',
    'PENDING': 'pending',
    'VERIFIED': 'verified',
    'FAILED': 'failed'
}

# Error Messages
ERROR_MESSAGES = {
    'INVALID_FILE': 'Invalid file format',
    'FILE_TOO_LARGE': 'File size exceeds maximum limit',
    'ENCRYPTION_FAILED': 'Failed to encrypt file',
    'DECRYPTION_FAILED': 'Failed to decrypt file',
    'SIGNATURE_FAILED': 'Digital signature verification failed',
    'KEY_NOT_FOUND': 'Public key not found',
    'INVALID_KEY': 'Invalid key format',
    'FILE_CORRUPTED': 'File integrity check failed - file may be corrupted'
}