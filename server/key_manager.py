# server/key_manager.py
"""
RSA Key Management Module
Handles generation, storage, and retrieval of RSA key pairs
"""

import os
import json
import base64
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes
from typing import Tuple, Optional, Dict

class KeyManager:
    def __init__(self, keys_directory: str = "keys"):
        """
        Initialize Key Manager
        
        Args:
            keys_directory: Directory to store keys
        """
        self.keys_directory = keys_directory
        self._ensure_directory_exists()
        
    def _ensure_directory_exists(self):
        """Create keys directory if it doesn't exist"""
        if not os.path.exists(self.keys_directory):
            os.makedirs(self.keys_directory)
            
    def generate_key_pair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """
        Generate RSA key pair
        
        Args:
            key_size: Size of the key (default 2048)
            
        Returns:
            Tuple of (private_key, public_key) in PEM format
        """
        # Generate private key
        private_key = RSA.generate(key_size)
        
        # Extract public key
        public_key = private_key.publickey()
        
        # Export keys in PEM format
        private_pem = private_key.export_key()
        public_pem = public_key.export_key()
        
        return private_pem, public_pem
    
    def save_key_pair(self, user_id: str, private_key: bytes, public_key: bytes) -> Dict[str, str]:
        """
        Save key pair to files
        
        Args:
            user_id: Unique identifier for the user
            private_key: Private key in PEM format
            public_key: Public key in PEM format
            
        Returns:
            Dictionary with file paths
        """
        # Create user directory
        user_dir = os.path.join(self.keys_directory, user_id)
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            
        # Save private key
        private_key_path = os.path.join(user_dir, "private_key.pem")
        with open(private_key_path, 'wb') as f:
            f.write(private_key)
            
        # Save public key
        public_key_path = os.path.join(user_dir, "public_key.pem")
        with open(public_key_path, 'wb') as f:
            f.write(public_key)
            
        # Save metadata
        metadata = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "key_size": RSA.import_key(private_key).size_in_bits(),
            "public_key_path": public_key_path,
            "private_key_path": private_key_path
        }
        
        metadata_path = os.path.join(user_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return {
            "private_key_path": private_key_path,
            "public_key_path": public_key_path,
            "metadata_path": metadata_path
        }
    
    def load_private_key(self, user_id: str) -> Optional[RSA.RsaKey]:
        """
        Load private key for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            RSA private key object or None if not found
        """
        private_key_path = os.path.join(self.keys_directory, user_id, "private_key.pem")
        
        if not os.path.exists(private_key_path):
            return None
            
        with open(private_key_path, 'rb') as f:
            private_key = RSA.import_key(f.read())
            
        return private_key
    
    def load_public_key(self, user_id: str) -> Optional[RSA.RsaKey]:
        """
        Load public key for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            RSA public key object or None if not found
        """
        public_key_path = os.path.join(self.keys_directory, user_id, "public_key.pem")
        
        if not os.path.exists(public_key_path):
            return None
            
        with open(public_key_path, 'rb') as f:
            public_key = RSA.import_key(f.read())
            
        return public_key
    
    def get_public_key_pem(self, user_id: str) -> Optional[str]:
        """
        Get public key in PEM format as string
        
        Args:
            user_id: User identifier
            
        Returns:
            Public key in PEM format or None
        """
        public_key = self.load_public_key(user_id)
        if public_key:
            return public_key.export_key().decode('utf-8')
        return None
    
    def import_public_key_from_pem(self, pem_key: str) -> RSA.RsaKey:
        """
        Import public key from PEM string
        
        Args:
            pem_key: Public key in PEM format
            
        Returns:
            RSA public key object
        """
        return RSA.import_key(pem_key.encode('utf-8'))
    
    def list_users(self) -> list:
        """
        List all users with stored keys
        
        Returns:
            List of user IDs
        """
        users = []
        if os.path.exists(self.keys_directory):
            for user_id in os.listdir(self.keys_directory):
                user_dir = os.path.join(self.keys_directory, user_id)
                if os.path.isdir(user_dir):
                    metadata_path = os.path.join(user_dir, "metadata.json")
                    if os.path.exists(metadata_path):
                        users.append(user_id)
        return users
    
    def delete_user_keys(self, user_id: str) -> bool:
        """
        Delete all keys for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        user_dir = os.path.join(self.keys_directory, user_id)
        
        if os.path.exists(user_dir):
            import shutil
            shutil.rmtree(user_dir)
            return True
        return False
    
    def export_public_keys_registry(self) -> Dict[str, str]:
        """
        Export all public keys as a registry
        
        Returns:
            Dictionary mapping user_id to public key PEM
        """
        registry = {}
        for user_id in self.list_users():
            public_key_pem = self.get_public_key_pem(user_id)
            if public_key_pem:
                registry[user_id] = public_key_pem
        return registry


# Utility functions for key operations
def generate_session_key() -> bytes:
    """Generate a random session key for hybrid encryption"""
    return get_random_bytes(32)  # 256-bit key for AES


def key_to_base64(key: bytes) -> str:
    """Convert key bytes to base64 string"""
    return base64.b64encode(key).decode('utf-8')


def base64_to_key(key_b64: str) -> bytes:
    """Convert base64 string to key bytes"""
    return base64.b64decode(key_b64.encode('utf-8'))