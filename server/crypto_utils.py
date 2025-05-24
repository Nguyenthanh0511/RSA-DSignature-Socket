# server/crypto_utils.py
"""
Cryptographic utilities for file encryption, decryption, and digital signatures
"""

import hashlib
import base64
from typing import Tuple, Optional
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class CryptoUtils:
    """Handles all cryptographic operations"""
    
    @staticmethod
    def hash_file(file_data: bytes) -> str:
        """
        Generate SHA-256 hash of file data
        
        Args:
            file_data: File content in bytes
            
        Returns:
            Hex string of hash
        """
        sha256_hash = hashlib.sha256()
        sha256_hash.update(file_data)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def encrypt_file(file_data: bytes, recipient_public_key: RSA.RsaKey) -> Tuple[bytes, bytes, bytes]:
        """
        Encrypt file using hybrid encryption (RSA + AES)
        
        Args:
            file_data: File content to encrypt
            recipient_public_key: Recipient's RSA public key
            
        Returns:
            Tuple of (encrypted_file, encrypted_aes_key, iv)
        """
        # Generate AES key and IV
        aes_key = get_random_bytes(32)  # 256-bit key
        iv = get_random_bytes(16)  # 128-bit IV
        
        # Encrypt file with AES
        cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
        padded_data = pad(file_data, AES.block_size)
        encrypted_file = cipher_aes.encrypt(padded_data)
        
        # Encrypt AES key with RSA
        cipher_rsa = PKCS1_OAEP.new(recipient_public_key)
        encrypted_aes_key = cipher_rsa.encrypt(aes_key)
        
        return encrypted_file, encrypted_aes_key, iv
    
    @staticmethod
    def decrypt_file(encrypted_file: bytes, encrypted_aes_key: bytes, 
                    iv: bytes, recipient_private_key: RSA.RsaKey) -> bytes:
        """
        Decrypt file using hybrid decryption
        
        Args:
            encrypted_file: Encrypted file content
            encrypted_aes_key: Encrypted AES key
            iv: Initialization vector
            recipient_private_key: Recipient's RSA private key
            
        Returns:
            Decrypted file content
        """
        # Decrypt AES key with RSA
        cipher_rsa = PKCS1_OAEP.new(recipient_private_key)
        aes_key = cipher_rsa.decrypt(encrypted_aes_key)
        
        # Decrypt file with AES
        cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
        decrypted_padded = cipher_aes.decrypt(encrypted_file)
        decrypted_file = unpad(decrypted_padded, AES.block_size)
        
        return decrypted_file
    
    @staticmethod
    def sign_data(data: bytes, private_key: RSA.RsaKey) -> bytes:
        """
        Create digital signature for data
        
        Args:
            data: Data to sign
            private_key: Signer's private key
            
        Returns:
            Digital signature
        """
        # Create hash of data
        h = SHA256.new(data)
        
        # Sign the hash
        signature = pkcs1_15.new(private_key).sign(h)
        
        return signature
    
    @staticmethod
    def verify_signature(data: bytes, signature: bytes, public_key: RSA.RsaKey) -> bool:
        """
        Verify digital signature
        
        Args:
            data: Original data
            signature: Digital signature to verify
            public_key: Signer's public key
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Create hash of data
        h = SHA256.new(data)
        
        try:
            # Verify signature
            pkcs1_15.new(public_key).verify(h, signature)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def encrypt_and_sign(file_data: bytes, sender_private_key: RSA.RsaKey, 
                        recipient_public_key: RSA.RsaKey) -> dict:
        """
        Encrypt file and create digital signature
        
        Args:
            file_data: File content to encrypt
            sender_private_key: Sender's private key for signing
            recipient_public_key: Recipient's public key for encryption
            
        Returns:
            Dictionary containing encrypted data and signature
        """
        # Hash the original file
        file_hash = CryptoUtils.hash_file(file_data)
        
        # Encrypt the file
        encrypted_file, encrypted_aes_key, iv = CryptoUtils.encrypt_file(
            file_data, recipient_public_key
        )
        
        # Sign the original file hash
        signature = CryptoUtils.sign_data(file_hash.encode(), sender_private_key)
        
        # Encode everything to base64 for transmission
        return {
            'encrypted_file': base64.b64encode(encrypted_file).decode('utf-8'),
            'encrypted_aes_key': base64.b64encode(encrypted_aes_key).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'signature': base64.b64encode(signature).decode('utf-8'),
            'file_hash': file_hash
        }
    
    @staticmethod
    def decrypt_and_verify(encrypted_data: dict, recipient_private_key: RSA.RsaKey,
                          sender_public_key: RSA.RsaKey) -> Tuple[bytes, bool, str]:
        """
        Decrypt file and verify digital signature
        
        Args:
            encrypted_data: Dictionary containing encrypted data
            recipient_private_key: Recipient's private key for decryption
            sender_public_key: Sender's public key for verification
            
        Returns:
            Tuple of (decrypted_file, is_valid, message)
        """
        try:
            # Decode from base64
            encrypted_file = base64.b64decode(encrypted_data['encrypted_file'])
            encrypted_aes_key = base64.b64decode(encrypted_data['encrypted_aes_key'])
            iv = base64.b64decode(encrypted_data['iv'])
            signature = base64.b64decode(encrypted_data['signature'])
            original_hash = encrypted_data['file_hash']
            
            # Decrypt the file
            decrypted_file = CryptoUtils.decrypt_file(
                encrypted_file, encrypted_aes_key, iv, recipient_private_key
            )
            
            # Verify file integrity
            decrypted_hash = CryptoUtils.hash_file(decrypted_file)
            
            # Verify signature
            is_signature_valid = CryptoUtils.verify_signature(
                original_hash.encode(), signature, sender_public_key
            )
            
            if not is_signature_valid:
                return decrypted_file, False, "Chữ ký số không hợp lệ!"
            
            if decrypted_hash != original_hash:
                return decrypted_file, False, "File đã bị thay đổi - không toàn vẹn!"
            
            return decrypted_file, True, "File toàn vẹn và chữ ký hợp lệ"
            
        except Exception as e:
            raise Exception(f"Lỗi giải mã hoặc xác thực: {str(e)}")


class SecureFileTransfer:
    """High-level interface for secure file transfer"""
    
    def __init__(self, key_manager):
        self.key_manager = key_manager
        self.crypto = CryptoUtils()
    
    def prepare_file_for_transfer(self, file_data: bytes, file_name: str,
                                 sender_id: str, recipient_id: str) -> dict:
        """
        Prepare file for secure transfer
        
        Args:
            file_data: File content
            file_name: Original file name
            sender_id: Sender's user ID
            recipient_id: Recipient's user ID
            
        Returns:
            Transfer package dictionary
        """
        # Load keys
        sender_private_key = self.key_manager.load_private_key(sender_id)
        recipient_public_key = self.key_manager.load_public_key(recipient_id)
        
        if not sender_private_key:
            raise ValueError(f"Private key not found for sender: {sender_id}")
        
        if not recipient_public_key:
            raise ValueError(f"Public key not found for recipient: {recipient_id}")
        
        # Encrypt and sign
        encrypted_package = self.crypto.encrypt_and_sign(
            file_data, sender_private_key, recipient_public_key
        )
        
        # Add metadata
        encrypted_package['file_name'] = file_name
        encrypted_package['sender_id'] = sender_id
        encrypted_package['recipient_id'] = recipient_id
        
        return encrypted_package
    
    def receive_and_process_file(self, transfer_package: dict) -> Tuple[bytes, str, bool, str]:
        """
        Receive and process transferred file
        
        Args:
            transfer_package: Transfer package from sender
            
        Returns:
            Tuple of (file_data, file_name, is_valid, message)
        """
        # Extract metadata
        sender_id = transfer_package['sender_id']
        recipient_id = transfer_package['recipient_id']
        file_name = transfer_package['file_name']
        
        # Load keys
        recipient_private_key = self.key_manager.load_private_key(recipient_id)
        sender_public_key = self.key_manager.load_public_key(sender_id)
        
        if not recipient_private_key:
            raise ValueError(f"Private key not found for recipient: {recipient_id}")
        
        if not sender_public_key:
            raise ValueError(f"Public key not found for sender: {sender_id}")
        
        # Decrypt and verify
        file_data, is_valid, message = self.crypto.decrypt_and_verify(
            transfer_package, recipient_private_key, sender_public_key
        )
        
        return file_data, file_name, is_valid, message