// client/static/js/main.js
/**
 * Main application logic
 */

// Global variables
let currentFile = null;
let currentFileContent = null;
let privateKey = null;
let currentTransferId = null;
let pendingTransfers = [];

/**
 * Initialize sender interface
 */
function initializeSenderInterface() {
    // Connect to WebSocket
    socketManager.connect();
    
    // Setup event handlers
    setupSenderEventHandlers();
    
    // Setup UI event listeners
    setupSenderUIListeners();
    
    // Setup socket event listeners
    setupSenderSocketListeners();
}

/**
 * Initialize receiver interface
 */
function initializeReceiverInterface() {
    // Connect to WebSocket
    socketManager.connect();
    
    // Setup event handlers
    setupReceiverEventHandlers();
    
    // Setup UI event listeners
    setupReceiverUIListeners();
    
    // Setup socket event listeners
    setupReceiverSocketListeners();
}

/**
 * Setup sender UI event listeners
 */
function setupSenderUIListeners() {
    // Register button
    document.getElementById('register-btn').addEventListener('click', () => {
        const userId = document.getElementById('sender-id').value.trim();
        if (userId) {
            socketManager.registerUser(userId);
            showStatus('Đang kết nối...', 'info');
        } else {
            showStatus('Vui lòng nhập ID người dùng', 'error');
        }
    });
    
    // File input
    document.getElementById('file-input').addEventListener('change', handleFileSelect);
    
    // Private key input
    document.getElementById('private-key-input').addEventListener('change', (e) => {
        privateKey = e.target.value.trim();
        if (privateKey) {
            showStatus('Đã nhập khóa riêng tư', 'success');
        }
    });
    
    // Get recipient key button
    document.getElementById('get-recipient-key-btn').addEventListener('click', () => {
        const recipientId = document.getElementById('recipient-id').value.trim();
        if (recipientId) {
            socketManager.requestPublicKey(recipientId);
            showStatus('Đang lấy khóa công khai...', 'info');
        } else {
            showStatus('Vui lòng nhập ID người nhận', 'error');
        }
    });
    
    // Save file changes button
    document.getElementById('save-changes-btn').addEventListener('click', () => {
        currentFileContent = document.getElementById('file-content').value;
        showStatus('Đã lưu thay đổi', 'success');
    });
    
    // Encrypt and send button
    document.getElementById('encrypt-and-send-btn').addEventListener('click', handleEncryptAndSend);
}

/**
 * Setup receiver UI event listeners
 */
function setupReceiverUIListeners() {
    // Register button
    document.getElementById('register-btn').addEventListener('click', () => {
        const userId = document.getElementById('receiver-id').value.trim();
        if (userId) {
            socketManager.registerUser(userId);
            showStatus('Đang kết nối...', 'info');
        } else {
            showStatus('Vui lòng nhập ID người dùng', 'error');
        }
    });
    
    // Private key input
    document.getElementById('private-key-input').addEventListener('change', (e) => {
        privateKey = e.target.value.trim();
        if (privateKey) {
            showStatus('Đã nhập khóa riêng tư', 'success');
        }
    });
    
    // Decrypt button
    document.getElementById('decrypt-btn').addEventListener('click', handleDecryptFile);
    
    // Continue decrypt button (for corrupted files)
    document.getElementById('continue-decrypt-btn').addEventListener('click', () => {
        document.getElementById('corruption-warning').style.display = 'none';
        performDecryption(true);
    });
    
    // Cancel decrypt button
    document.getElementById('cancel-decrypt-btn').addEventListener('click', () => {
        document.getElementById('corruption-warning').style.display = 'none';
        document.getElementById('process-section').style.display = 'none';
    });
}

/**
 * Setup sender socket event listeners
 */
function setupSenderSocketListeners() {
    socketManager.on('connection_status', (data) => {
        if (data.connected) {
            showStatus('Đã kết nối với server', 'success');
        } else {
            showStatus('Mất kết nối với server', 'error');
        }
    });
    
    socketManager.on('user_registered', (data) => {
        if (data.status === 'success') {
            showStatus('Đăng ký thành công!', 'success');
            document.getElementById('key-section').style.display = 'block';
            document.getElementById('file-section').style.display = 'block';
            document.getElementById('recipient-section').style.display = 'block';
            document.getElementById('history-section').style.display = 'block';
            
            // Get online users and transfer history
            socketManager.getOnlineUsers();
            socketManager.getTransferHistory();
        }
    });
    
    socketManager.on('keys_generated', (data) => {
        if (data.status === 'success') {
            document.getElementById('public-key-display').value = data.public_key;
            showStatus('Khóa đã được tạo thành công!', 'success');
        }
    });
    
    socketManager.on('public_key_received', (data) => {
        if (data.status === 'success') {
            document.getElementById('recipient-key-info').style.display = 'block';
            document.getElementById('send-section').style.display = 'block';
            updateSendSummary();
            showStatus('Đã lấy khóa công khai của người nhận', 'success');
        } else {
            showStatus('Không tìm thấy khóa công khai', 'error');
        }
    });
    
    socketManager.on('file_sent', (data) => {
        if (data.status === 'success') {
            showStatus('File đã được gửi thành công!', 'success');
            updateProgress(100, 'Hoàn thành!');
            
            // Refresh transfer history
            socketManager.getTransferHistory();
            
            // Reset form
            setTimeout(() => {
                resetSenderForm();
            }, 2000);
        }
    });
    
    socketManager.on('online_users_updated', (users) => {
        updateOnlineUsersList(users);
    });
    
    socketManager.on('transfer_history_received', (data) => {
        updateTransferHistory(data.sent, 'sent');
    });
}

/**
 * Setup receiver socket event listeners
 */
function setupReceiverSocketListeners() {
    socketManager.on('connection_status', (data) => {
        if (data.connected) {
            showStatus('Đã kết nối với server', 'success');
        } else {
            showStatus('Mất kết nối với server', 'error');
        }
    });
    
    socketManager.on('user_registered', (data) => {
        if (data.status === 'success') {
            showStatus('Đăng ký thành công!', 'success');
            document.getElementById('key-section').style.display = 'block';
            document.getElementById('received-files-section').style.display = 'block';
            document.getElementById('history-section').style.display = 'block';
            
            // Get transfer history
            socketManager.getTransferHistory();
        }
    });
    
    socketManager.on('keys_generated', (data) => {
        if (data.status === 'success') {
            document.getElementById('public-key-display').value = data.public_key;
            showStatus('Khóa đã được tạo thành công!', 'success');
        }
    });
    
    socketManager.on('file_received', (data) => {
        showStatus(`Nhận được file mới từ ${data.sender_id}`, 'info');
        addReceivedFile(data);
        
        // Show notification
        if (Notification.permission === 'granted') {
            new Notification('File mới', {
                body: `Bạn nhận được file từ ${data.sender_id}`,
                icon: '📥'
            });
        }
    });
    
    socketManager.on('file_download_ready', (data) => {
        if (data.status === 'success') {
            currentTransferId = data.transfer_id;
            window.currentEncryptedPackage = data.encrypted_package;
            window.currentSenderId = data.sender_id;
            
            document.getElementById('process-section').style.display = 'block';
            document.getElementById('process-file-name').textContent = data.encrypted_package.file_name;
            document.getElementById('process-sender').textContent = data.sender_id;
            document.getElementById('process-time').textContent = new Date().toLocaleString('vi-VN');
        }
    });
    
    socketManager.on('transfer_history_received', (data) => {
        updateTransferHistory(data.received, 'received');
        
        // Also update received files list
        data.received.forEach(transfer => {
            if (transfer.status === 'pending') {
                addReceivedFile(transfer);
            }
        });
    });
}

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    currentFile = file;
    
    // Display file info
    document.getElementById('file-info').innerHTML = `
        <div class="alert alert-info">
            <p><strong>File:</strong> ${file.name}</p>
            <p><strong>Kích thước:</strong> ${formatFileSize(file.size)}</p>
            <p><strong>Loại:</strong> ${file.type || 'Unknown'}</p>
        </div>
    `;
    
    // Read file content
    const reader = new FileReader();
    reader.onload = (e) => {
        currentFileContent = e.target.result;
        
        // Show editor for text files
        if (file.type.startsWith('text/') || file.name.endsWith('.txt') || 
            file.name.endsWith('.json') || file.name.endsWith('.xml')) {
            document.getElementById('file-editor').style.display = 'block';
            document.getElementById('file-content').value = currentFileContent;
        } else {
            document.getElementById('file-editor').style.display = 'none';
        }
    };
    
    // Read as text for text files, as base64 for binary files
    if (file.type.startsWith('text/') || file.name.endsWith('.txt') || 
        file.name.endsWith('.json') || file.name.endsWith('.xml')) {
        reader.readAsText(file);
    } else {
        reader.readAsDataURL(file);
    }
}

/**
 * Handle encrypt and send
 */
async function handleEncryptAndSend() {
    if (!currentFile || !currentFileContent) {
        showStatus('Vui lòng chọn file', 'error');
        return;
    }
    
    if (!privateKey) {
        showStatus('Vui lòng nhập khóa riêng tư', 'error');
        return;
    }
    
    const recipientId = document.getElementById('recipient-id').value.trim();
    if (!recipientId) {
        showStatus('Vui lòng nhập ID người nhận', 'error');
        return;
    }
    
    if (!socketManager.recipientPublicKey) {
        showStatus('Vui lòng lấy khóa công khai của người nhận', 'error');
        return;
    }
    
    try {
        // Show progress
        document.getElementById('send-progress').style.display = 'block';
        updateProgress(20, 'Đang mã hóa file...');
        
        // Encrypt file
        const encryptedPackage = cryptoClient.hybridEncrypt(
            currentFileContent,
            socketManager.recipientPublicKey,
            privateKey
        );
        
        updateProgress(50, 'Đang ký số...');
        
        // Add metadata
        encryptedPackage.file_name = currentFile.name;
        encryptedPackage.file_size = currentFile.size;
        encryptedPackage.timestamp = new Date().toISOString();
        
        updateProgress(70, 'Đang gửi file...');
        
        // Send file
        socketManager.sendFile(recipientId, encryptedPackage);
        
        updateProgress(90, 'Đang xác nhận...');
        
    } catch (error) {
        console.error('Encryption error:', error);
        showStatus('Lỗi mã hóa file: ' + error.message, 'error');
        document.getElementById('send-progress').style.display = 'none';
    }
}

/**
 * Handle decrypt file
 */
function handleDecryptFile() {
    if (!privateKey) {
        showStatus('Vui lòng nhập khóa riêng tư', 'error');
        return;
    }
    
    if (!window.currentEncryptedPackage) {
        showStatus('Không có file để giải mã', 'error');
        return;
    }
    
    performDecryption(false);
}

/**
 * Perform decryption
 */
async function performDecryption(forceContinue) {
    try {
        document.getElementById('decrypt-progress').style.display = 'block';
        updateDecryptProgress(20, 'Đang lấy khóa công khai người gửi...');
        
        // Get sender's public key
        await new Promise((resolve) => {
            socketManager.on('public_key_received', (data) => {
                if (data.status === 'success') {
                    resolve();
                }
            });
            socketManager.requestPublicKey(window.currentSenderId);
        });
        
        updateDecryptProgress(40, 'Đang giải mã file...');
        
        // Decrypt file
        const result = cryptoClient.hybridDecrypt(
            window.currentEncryptedPackage,
            privateKey,
            socketManager.recipientPublicKey
        );
        
        updateDecryptProgress(70, 'Đang xác thực chữ ký...');
        
        // Check if file is corrupted
        if (!result.integrityValid && !forceContinue) {
            document.getElementById('corruption-warning').style.display = 'block';
            document.getElementById('decrypt-progress').style.display = 'none';
            return;
        }
        
        updateDecryptProgress(90, 'Hoàn thành!');
        
        // Show results
        showDecryptionResults(result);
        
        // Report to server
        socketManager.reportDecryptionResult(currentTransferId, result);
        
        // Save decrypted content
        window.decryptedContent = result.fileContent;
        
    } catch (error) {
        console.error('Decryption error:', error);
        showStatus('Lỗi giải mã: ' + error.message, 'error');
        document.getElementById('decrypt-progress').style.display = 'none';
    }
}

/**
 * Show decryption results
 */
function showDecryptionResults(result) {
    document.getElementById('decrypt-results').style.display = 'block';
    
    // Signature status
    const signatureEl = document.getElementById('signature-status');
    const signatureResult = document.getElementById('signature-result');
    
    if (result.signatureValid) {
        signatureEl.className = 'alert alert-success';
        signatureResult.textContent = 'Hợp lệ ✅';
    } else {
        signatureEl.className = 'alert alert-error';
        signatureResult.textContent = 'Không hợp lệ ❌';
    }
    
    // Integrity status
    const integrityEl = document.getElementById('integrity-status');
    const integrityResult = document.getElementById('integrity-result');
    
    if (result.integrityValid) {
        integrityEl.className = 'alert alert-success';
        integrityResult.textContent = 'File toàn vẹn ✅';
    } else {
        integrityEl.className = 'alert alert-warning';
        integrityResult.textContent = 'File đã bị thay đổi ⚠️';
    }
    
    // Show file actions
    if (result.success) {
        document.getElementById('file-actions').style.display = 'block';
        
        // Setup download button
        document.getElementById('download-btn').onclick = () => {
            downloadDecryptedFile(result.fileContent, window.currentEncryptedPackage.file_name);
        };
        
        // Show view button for text files
        const fileName = window.currentEncryptedPackage.file_name;
        if (fileName.endsWith('.txt') || fileName.endsWith('.json') || fileName.endsWith('.xml')) {
            document.getElementById('view-content-btn').style.display = 'inline-block';
            document.getElementById('view-content-btn').onclick = () => {
                document.getElementById('file-viewer').style.display = 'block';
                document.getElementById('file-content-view').value = result.fileContent;
            };
        }
    }
    
    document.getElementById('decrypt-progress').style.display = 'none';
}

/**
 * Utility functions
 */

function showStatus(message, type) {
    const statusEl = document.getElementById('connection-status') || 
                    document.getElementById('send-result') ||
                    document.getElementById('decrypt-results');
    
    if (statusEl) {
        statusEl.className = `alert alert-${type}`;
        statusEl.textContent = message;
        statusEl.style.display = 'block';
    }
}

function updateProgress(percent, status) {
    const progressBar = document.querySelector('.progress-bar');
    const progressStatus = document.getElementById('progress-status');
    
    if (progressBar) {
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
    }
    
    if (progressStatus) {
        progressStatus.textContent = status;
    }
}

function updateDecryptProgress(percent, status) {
    const progressBar = document.querySelector('#decrypt-progress .progress-bar');
    const progressStatus = document.querySelector('#decrypt-progress #progress-status');
    
    if (progressBar) {
        progressBar.style.width = percent + '%';
        progressBar.textContent = percent + '%';
    }
    
    if (progressStatus) {
        progressStatus.textContent = status;
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function updateSendSummary() {
    const recipientId = document.getElementById('recipient-id').value.trim();
    document.getElementById('send-file-name').textContent = currentFile ? currentFile.name : 'N/A';
    document.getElementById('send-file-size').textContent = currentFile ? formatFileSize(currentFile.size) : 'N/A';
    document.getElementById('send-recipient').textContent = recipientId || 'N/A';
}

function updateOnlineUsersList(users) {
    const listEl = document.getElementById('online-users-list');
    if (!listEl) return;
    
    if (users.length === 0) {
        listEl.innerHTML = '<p style="text-align: center; color: #666;">Không có người dùng online</p>';
        return;
    }
    
    listEl.innerHTML = users.map(user => `
        <div class="user-item">
            <span>
                <span class="user-status status-online"></span>
                ${user.username} (${user.user_id})
            </span>
            <button class="btn btn-sm" onclick="selectRecipient('${user.user_id}')">
                Chọn
            </button>
        </div>
    `).join('');
}

function selectRecipient(userId) {
    document.getElementById('recipient-id').value = userId;
    document.getElementById('get-recipient-key-btn').click();
}

function addReceivedFile(transfer) {
    const listEl = document.getElementById('received-files-list');
    if (!listEl) return;
    
    // Remove placeholder text
    if (listEl.querySelector('p')) {
        listEl.innerHTML = '';
    }
    
    // Add file to list
    const fileEl = document.createElement('div');
    fileEl.className = 'transfer-item';
    fileEl.innerHTML = `
        <div>${transfer.file_name || 'Unknown'}</div>
        <div>Từ: ${transfer.sender_id}</div>
        <div>${new Date(transfer.timestamp || transfer.created_at).toLocaleString('vi-VN')}</div>
        <div>
            <button class="btn btn-primary btn-sm" onclick="downloadTransferFile('${transfer.transfer_id}')">
                Tải về & Giải mã
            </button>
        </div>
    `;
    
    listEl.appendChild(fileEl);
}

function downloadTransferFile(transferId) {
    socketManager.downloadFile(transferId);
}

function updateTransferHistory(transfers, type) {
    const listEl = document.getElementById('transfer-history-list');
    if (!listEl) return;
    
    if (transfers.length === 0) {
        listEl.innerHTML = `<p style="text-align: center; color: #666;">Chưa có lịch sử ${type === 'sent' ? 'gửi' : 'nhận'} file</p>`;
        return;
    }
    
    listEl.innerHTML = transfers.map(transfer => `
        <div class="transfer-item">
            <div>${transfer.file_name}</div>
            <div>${type === 'sent' ? 'Đến' : 'Từ'}: ${type === 'sent' ? transfer.recipient_id : transfer.sender_id}</div>
            <div>${new Date(transfer.created_at).toLocaleString('vi-VN')}</div>
            <div>
                <span class="status-badge status-${transfer.status}">${getStatusText(transfer.status)}</span>
            </div>
        </div>
    `).join('');
}

function getStatusText(status) {
    const statusMap = {
        'success': 'Thành công',
        'pending': 'Đang chờ',
        'failed': 'Thất bại',
        'error': 'Lỗi'
    };
    return statusMap[status] || status;
}

function resetSenderForm() {
    document.getElementById('file-input').value = '';
    document.getElementById('file-info').innerHTML = '';
    document.getElementById('file-editor').style.display = 'none';
    document.getElementById('recipient-id').value = '';
    document.getElementById('recipient-key-info').style.display = 'none';
    document.getElementById('send-section').style.display = 'none';
    document.getElementById('send-progress').style.display = 'none';
    currentFile = null;
    currentFileContent = null;
    socketManager.recipientPublicKey = null;
}

function downloadDecryptedFile(content, filename) {
    // Check if content is base64 encoded (for binary files)
    let blob;
    if (content.startsWith('data:')) {
        // Extract base64 data
        const base64Data = content.split(',')[1];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        blob = new Blob([byteArray]);
    } else {
        // Text file
        blob = new Blob([content], { type: 'text/plain' });
    }
    
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// Setup event handlers (empty functions to be filled by specific interfaces)
function setupSenderEventHandlers() {
    // Additional sender-specific handlers can be added here
}

function setupReceiverEventHandlers() {
    // Additional receiver-specific handlers can be added here
}

// Request notification permission
if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

// Auto-refresh online users every 30 seconds
setInterval(() => {
    if (socketManager.connected && socketManager.userId) {
        socketManager.getOnlineUsers();
    }
}, 30000);

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && socketManager.connected) {
        // Refresh data when page becomes visible
        socketManager.getTransferHistory();
        socketManager.getOnlineUsers();
    }
});

// Export functions for global access
window.selectRecipient = selectRecipient;
window.downloadTransferFile = downloadTransferFile;