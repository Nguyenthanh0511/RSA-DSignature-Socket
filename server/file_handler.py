# server/file_handler.py
"""
File handling utilities
"""

import os
import uuid
import json
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from typing import Optional, Tuple
from shared.constants import ALLOWED_EXTENSIONS, MAX_FILE_SIZE


class FileHandler:
    """Handles file operations"""
    
    def __init__(self, upload_folder: str = "uploads"):
        self.upload_folder = upload_folder
        self._ensure_upload_folder()
    
    def _ensure_upload_folder(self):
        """Create upload folder if it doesn't exist"""
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def allowed_file(self, filename: str) -> bool:
        """
        Check if file extension is allowed
        
        Args:
            filename: Name of the file
            
        Returns:
            True if allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def save_uploaded_file(self, file_data: bytes, filename: str, 
                          user_id: str) -> Tuple[str, str, int]:
        """
        Save uploaded file to disk
        
        Args:
            file_data: File content in bytes
            filename: Original filename
            user_id: User who uploaded the file
            
        Returns:
            Tuple of (file_id, file_path, file_size)
        """
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Secure the filename
        safe_filename = secure_filename(filename)
        
        # Create user upload directory
        user_dir = os.path.join(self.upload_folder, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
        
        # Create file directory
        file_dir = os.path.join(user_dir, file_id)
        os.makedirs(file_dir)
        
        # Save original file
        file_path = os.path.join(file_dir, safe_filename)
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Save metadata
        metadata = {
            'file_id': file_id,
            'original_name': filename,
            'safe_name': safe_filename,
            'size': len(file_data),
            'upload_time': datetime.now().isoformat(),
            'user_id': user_id
        }
        
        metadata_path = os.path.join(file_dir, 'metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return file_id, file_path, len(file_data)
    
    def save_encrypted_file(self, encrypted_data: dict, transfer_id: str) -> str:
        """
        Save encrypted file data
        
        Args:
            encrypted_data: Dictionary containing encrypted file data
            transfer_id: Unique transfer ID
            
        Returns:
            Path to saved encrypted file
        """
        # Create encrypted files directory
        encrypted_dir = os.path.join(self.upload_folder, 'encrypted', transfer_id)
        if not os.path.exists(encrypted_dir):
            os.makedirs(encrypted_dir)
        
        # Save encrypted data as JSON
        encrypted_path = os.path.join(encrypted_dir, 'encrypted_package.json')
        with open(encrypted_path, 'w') as f:
            json.dump(encrypted_data, f)
        
        return encrypted_path
    
    def load_encrypted_file(self, transfer_id: str) -> Optional[dict]:
        """
        Load encrypted file data
        
        Args:
            transfer_id: Unique transfer ID
            
        Returns:
            Encrypted data dictionary or None
        """
        encrypted_path = os.path.join(self.upload_folder, 'encrypted', 
                                     transfer_id, 'encrypted_package.json')
        
        if os.path.exists(encrypted_path):
            with open(encrypted_path, 'r') as f:
                return json.load(f)
        
        return None
    
    def save_decrypted_file(self, file_data: bytes, filename: str, 
                           user_id: str, transfer_id: str) -> str:
        """
        Save decrypted file
        
        Args:
            file_data: Decrypted file content
            filename: Original filename
            user_id: Recipient user ID
            transfer_id: Transfer ID
            
        Returns:
            Path to saved file
        """
        # Create decrypted files directory
        decrypted_dir = os.path.join(self.upload_folder, 'decrypted', 
                                    user_id, transfer_id)
        if not os.path.exists(decrypted_dir):
            os.makedirs(decrypted_dir)
        
        # Save file
        safe_filename = secure_filename(filename)
        file_path = os.path.join(decrypted_dir, safe_filename)
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        return file_path
    
    def get_file_content(self, file_path: str) -> Optional[bytes]:
        """
        Read file content
        
        Args:
            file_path: Path to file
            
        Returns:
            File content in bytes or None
        """
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return f.read()
        return None
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file
        
        Args:
            file_path: Path to file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception:
            pass
        return False
    
    def cleanup_old_files(self, days: int = 7):
        """
        Clean up files older than specified days
        
        Args:
            days: Number of days to keep files
        """
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        
        for root, dirs, files in os.walk(self.upload_folder):
            for file in files:
                file_path = os.path.join(root, file)
                file_stat = os.stat(file_path)
                
                if file_stat.st_mtime < cutoff_time:
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
    
    def get_file_info(self, file_path: str) -> dict:
        """
        Get file information
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file info
        """
        if not os.path.exists(file_path):
            return {}
        
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'exists': True
        }
    
    def validate_file_size(self, file_size: int) -> Tuple[bool, str]:
        """
        Validate file size
        
        Args:
            file_size: Size of file in bytes
            
        Returns:
            Tuple of (is_valid, message)
        """
        if file_size > MAX_FILE_SIZE:
            return False, f"File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, "File size is valid"