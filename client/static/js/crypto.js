// client/static/js/crypto.js
/**
 * Cryptographic utilities for client-side encryption/decryption
 */

class CryptoClient {
    constructor() {
        this.jsEncrypt = new JSEncrypt();
    }

    /**
     * Generate RSA key pair
     * @param {number} keySize - Key size in bits
     * @returns {Object} Object containing publicKey and privateKey
     */
    generateKeyPair(keySize = 2048) {
        const crypt = new JSEncrypt({ default_key_size: keySize });
        const privateKey = crypt.getPrivateKey();
        const publicKey = crypt.getPublicKey();
        
        return {
            privateKey: privateKey,
            publicKey: publicKey
        };
    }

    /**
     * Encrypt data with RSA public key
     * @param {string} data - Data to encrypt
     * @param {string} publicKey - RSA public key in PEM format
     * @returns {string} Base64 encoded encrypted data
     */
    encryptWithPublicKey(data, publicKey) {
        const encrypt = new JSEncrypt();
        encrypt.setPublicKey(publicKey);
        return encrypt.encrypt(data);
    }

    /**
     * Decrypt data with RSA private key
     * @param {string} encryptedData - Base64 encoded encrypted data
     * @param {string} privateKey - RSA private key in PEM format
     * @returns {string} Decrypted data
     */
    decryptWithPrivateKey(encryptedData, privateKey) {
        const decrypt = new JSEncrypt();
        decrypt.setPrivateKey(privateKey);
        return decrypt.decrypt(encryptedData);
    }

    /**
     * Create digital signature
     * @param {string} data - Data to sign
     * @param {string} privateKey - Private key for signing
     * @returns {string} Base64 encoded signature
     */
    signData(data, privateKey) {
        const sign = new JSEncrypt();
        sign.setPrivateKey(privateKey);
        // JSEncrypt doesn't support signing directly, so we'll use a workaround
        // In production, use a proper RSA signing library
        const hash = CryptoJS.SHA256(data).toString();
        return sign.encrypt(hash);
    }

    /**
     * Verify digital signature
     * @param {string} data - Original data
     * @param {string} signature - Signature to verify
     * @param {string} publicKey - Public key for verification
     * @returns {boolean} True if signature is valid
     */
    verifySignature(data, signature, publicKey) {
        const verify = new JSEncrypt();
        verify.setPublicKey(publicKey);
        try {
            const decryptedHash = verify.decrypt(signature);
            const dataHash = CryptoJS.SHA256(data).toString();
            return decryptedHash === dataHash;
        } catch (e) {
            return false;
        }
    }

    /**
     * Generate AES key for hybrid encryption
     * @returns {string} Random AES key
     */
    generateAESKey() {
        return CryptoJS.lib.WordArray.random(256/8).toString();
    }

    /**
     * Encrypt file with AES (for large files)
     * @param {string} fileContent - File content to encrypt
     * @param {string} aesKey - AES key
     * @returns {Object} Object containing encrypted data and IV
     */
    encryptFileWithAES(fileContent, aesKey) {
        const iv = CryptoJS.lib.WordArray.random(128/8);
        const encrypted = CryptoJS.AES.encrypt(fileContent, CryptoJS.enc.Hex.parse(aesKey), {
            iv: iv,
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
        });

        return {
            encryptedData: encrypted.toString(),
            iv: iv.toString()
        };
    }

    /**
     * Decrypt file with AES
     * @param {string} encryptedData - Encrypted file data
     * @param {string} aesKey - AES key
     * @param {string} iv - Initialization vector
     * @returns {string} Decrypted file content
     */
    decryptFileWithAES(encryptedData, aesKey, iv) {
        const decrypted = CryptoJS.AES.decrypt(encryptedData, CryptoJS.enc.Hex.parse(aesKey), {
            iv: CryptoJS.enc.Hex.parse(iv),
            mode: CryptoJS.mode.CBC,
            padding: CryptoJS.pad.Pkcs7
        });

        return decrypted.toString(CryptoJS.enc.Utf8);
    }

    /**
     * Hybrid encryption for large files
     * @param {string} fileContent - File content
     * @param {string} recipientPublicKey - Recipient's public key
     * @param {string} senderPrivateKey - Sender's private key for signing
     * @returns {Object} Encrypted package
     */
    hybridEncrypt(fileContent, recipientPublicKey, senderPrivateKey) {
        // Generate AES key
        const aesKey = this.generateAESKey();
        
        // Encrypt file with AES
        const { encryptedData, iv } = this.encryptFileWithAES(fileContent, aesKey);
        
        // Encrypt AES key with RSA
        const encryptedAESKey = this.encryptWithPublicKey(aesKey, recipientPublicKey);
        
        // Create file hash
        const fileHash = CryptoJS.SHA256(fileContent).toString();
        
        // Sign the hash
        const signature = this.signData(fileContent, senderPrivateKey);
        
        return {
            encryptedFile: encryptedData,
            encryptedAESKey: encryptedAESKey,
            iv: iv,
            signature: signature,
            fileHash: fileHash
        };
    }

    /**
     * Hybrid decryption for large files
     * @param {Object} encryptedPackage - Encrypted package
     * @param {string} recipientPrivateKey - Recipient's private key
     * @param {string} senderPublicKey - Sender's public key for verification
     * @returns {Object} Decryption result
     */
    hybridDecrypt(encryptedPackage, recipientPrivateKey, senderPublicKey) {
        try {
            // Decrypt AES key
            const aesKey = this.decryptWithPrivateKey(
                encryptedPackage.encryptedAESKey, 
                recipientPrivateKey
            );
            
            if (!aesKey) {
                throw new Error('Failed to decrypt AES key');
            }
            
            // Decrypt file
            const decryptedFile = this.decryptFileWithAES(
                encryptedPackage.encryptedFile,
                aesKey,
                encryptedPackage.iv
            );
            
            // Verify signature
            const isSignatureValid = this.verifySignature(
                decryptedFile,
                encryptedPackage.signature,
                senderPublicKey
            );
            
            // Verify integrity
            const decryptedHash = CryptoJS.SHA256(decryptedFile).toString();
            const isIntegrityValid = decryptedHash === encryptedPackage.fileHash;
            
            return {
                success: true,
                fileContent: decryptedFile,
                signatureValid: isSignatureValid,
                integrityValid: isIntegrityValid,
                message: this.getVerificationMessage(isSignatureValid, isIntegrityValid)
            };
            
        } catch (error) {
            return {
                success: false,
                fileContent: null,
                signatureValid: false,
                integrityValid: false,
                message: `Decryption failed: ${error.message}`
            };
        }
    }

    /**
     * Get verification message based on signature and integrity
     */
    getVerificationMessage(signatureValid, integrityValid) {
        if (signatureValid && integrityValid) {
            return 'File toàn vẹn và chữ ký hợp lệ ✅';
        } else if (!signatureValid && integrityValid) {
            return 'Chữ ký không hợp lệ ⚠️';
        } else if (signatureValid && !integrityValid) {
            return 'File đã bị thay đổi - không toàn vẹn ❌';
        } else {
            return 'Chữ ký không hợp lệ và file không toàn vẹn ❌';
        }
    }

    /**
     * Calculate file hash
     * @param {string} fileContent - File content
     * @returns {string} SHA-256 hash
     */
    calculateFileHash(fileContent) {
        return CryptoJS.SHA256(fileContent).toString();
    }
}

// Initialize crypto client
const cryptoClient = new CryptoClient();