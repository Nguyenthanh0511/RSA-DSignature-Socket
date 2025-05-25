// client/static/js/socket.js
/**
 * WebSocket communication handler
 */

class SocketManager {
    constructor() {
        this.socket = null;
        this.connected = false;
        this.userId = null;
        this.publicKey = null;
        this.recipientPublicKey = null;
        this.eventHandlers = {};
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        this.socket = io({
            transports: ['websocket'],
            reconnection: true,
            reconnectionAttempts: 5,
            reconnectionDelay: 1000
        });

        this.setupEventHandlers();
        return this.socket;
    }

    /**
     * Setup socket event handlers
     */
    setupEventHandlers() {
        // Connection events
        this.socket.on('connect', () => {
            this.connected = true;
            console.log('Connected to server');
            this.emit('connection_status', { connected: true });
        });

        this.socket.on('disconnect', () => {
            this.connected = false;
            console.log('Disconnected from server');
            this.emit('connection_status', { connected: false });
        });

        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
            this.emit('socket_error', error);
        });

        // Custom events
        this.socket.on('connected', (data) => {
            this.emit('server_connected', data);
        });

        this.socket.on('user_registered', (data) => {
            this.emit('user_registered', data);
        });

        this.socket.on('keys_generated', (data) => {
            this.publicKey = data.public_key;
            this.emit('keys_generated', data);
        });

        this.socket.on('public_key_response', (data) => {
            if (data.status === 'success') {
                this.recipientPublicKey = data.public_key;
            }
            this.emit('public_key_received', data);
        });

        this.socket.on('file_sent', (data) => {
            this.emit('file_sent', data);
        });

        this.socket.on('file_received', (data) => {
            this.emit('file_received', data);
        });

        this.socket.on('file_download_response', (data) => {
            this.emit('file_download_ready', data);
        });

        this.socket.on('transfer_completed', (data) => {
            this.emit('transfer_completed', data);
        });

        this.socket.on('online_users_response', (data) => {
            this.emit('online_users_updated', data.users);
        });

        this.socket.on('transfer_history_response', (data) => {
            this.emit('transfer_history_received', data);
        });
    }

    /**
     * Register user with server
     */
    registerUser(userId, username) {
        this.userId = userId;
        this.socket.emit('register_user', {
            user_id: userId,
            username: username || userId
        });
    }

    /**
     * Request public key for a user
     */
    requestPublicKey(userId) {
        this.socket.emit('request_public_key', {
            user_id: userId
        });
    }

    /**
     * Send encrypted file
     */
    sendFile(recipientId, encryptedPackage) {
        this.socket.emit('send_file', {
            recipient_id: recipientId,
            encrypted_package: encryptedPackage
        });
    }

    /**
     * Download file by transfer ID
     */
    downloadFile(transferId) {
        this.socket.emit('download_file', {
            transfer_id: transferId
        });
    }

    /**
     * Report decryption result
     */
    reportDecryptionResult(transferId, result) {
        this.socket.emit('report_decryption_result', {
            transfer_id: transferId,
            success: result.success,
            signature_valid: result.signatureValid,
            integrity_valid: result.integrityValid,
            error_message: result.message
        });
    }

    /**
     * Get online users
     */
    getOnlineUsers() {
        this.socket.emit('get_online_users');
    }

    /**
     * Get transfer history
     */
    getTransferHistory() {
        this.socket.emit('get_transfer_history');
    }

    /**
     * Register event handler
     */
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    /**
     * Emit event to registered handlers
     */
    emit(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => handler(data));
        }
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Initialize socket manager
const socketManager = new SocketManager();