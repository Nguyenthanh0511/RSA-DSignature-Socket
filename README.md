# 🔐 Hệ thống truyền file bảo mật với RSA và chữ ký số

Hệ thống truyền file an toàn sử dụng mã hóa RSA, chữ ký số và WebSocket để đảm bảo tính bảo mật và toàn vẹn dữ liệu.

## 📋 Tính năng chính

- ✅ **Mã hóa RSA 2048-bit**: Bảo vệ file với thuật toán mã hóa mạnh
- ✅ **Chữ ký số**: Xác thực nguồn gốc và đảm bảo file không bị thay đổi
- ✅ **Hybrid Encryption**: Kết hợp RSA và AES cho file lớn
- ✅ **Real-time Communication**: Sử dụng WebSocket để truyền file nhanh chóng
- ✅ **Chỉnh sửa file**: Cho phép người gửi chỉnh sửa nội dung file trước khi gửi
- ✅ **Kiểm tra toàn vẹn**: Cảnh báo khi file bị thay đổi trong quá trình truyền
- ✅ **Lịch sử truyền file**: Theo dõi tất cả file đã gửi/nhận
- ✅ **Danh sách người dùng online**: Xem ai đang trực tuyến

## 🚀 Cài đặt nhanh

### Yêu cầu hệ thống
- Python 3.8+
- pip
- Browser hiện đại (Chrome, Firefox, Safari, Edge)

### Bước 1: Clone repository
```bash
git clone https://github.com/yourusername/secure-file-transfer.git
cd secure-file-transfer
```

### Bước 2: Tạo môi trường ảo (khuyến nghị)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Cấu hình môi trường
```bash
# Copy file .env mẫu
cp .env.example .env

# Chỉnh sửa file .env theo nhu cầu
# Mặc định có thể chạy ngay không cần chỉnh sửa
```

### Bước 5: Chạy ứng dụng
```bash
python run.py
```

Mở browser và truy cập: http://localhost:5000

## 📖 Hướng dẫn sử dụng

### Người gửi file
<img src="./sender.jpg">
1. **Truy cập trang Người gửi**
   - Từ trang chủ, click vào "Người gửi"

2. **Đăng ký/Kết nối**
   - Nhập ID người dùng (ví dụ: alice)
   - Click "Đăng ký / Kết nối"
   - Hệ thống sẽ tự động tạo cặp khóa RSA

3. **Nhập khóa riêng tư**
   - Copy khóa riêng tư từ hệ thống hoặc sử dụng khóa có sẵn
   - Paste vào ô "Nhập khóa riêng tư"

4. **Chọn file để gửi**
   - Click "Chọn file"
   - Chọn file từ máy tính (hỗ trợ: txt, pdf, png, jpg, doc, json, xml...)
   - Với file text: có thể chỉnh sửa nội dung trước khi gửi

5. **Chọn người nhận**
   - Nhập ID người nhận (ví dụ: bob)
   - Click "Lấy khóa công khai"
   - Hoặc chọn từ danh sách người dùng online

6. **Mã hóa và gửi**
   - Click "Mã hóa và gửi"
   - Theo dõi tiến trình qua progress bar
   - Nhận thông báo khi gửi thành công
<img src="./senderEn.jpg">
### Người nhận file

1. **Truy cập trang Người nhận**
   - Từ trang chủ, click vào "Người nhận"

2. **Đăng ký/Kết nối**
   - Nhập ID người dùng (ví dụ: bob)
   - Click "Đăng ký / Kết nối"

3. **Nhập khóa riêng tư**
   - Nhập khóa riêng tư của bạn

4. **Xem file đã nhận**
   - File nhận được sẽ hiển thị trong danh sách
   - Click "Tải về & Giải mã" để xử lý file

5. **Giải mã và xác thực**
   - Hệ thống sẽ tự động:
     - Xác thực chữ ký số
     - Kiểm tra tính toàn vẹn
     - Giải mã file
   - Xem kết quả xác thực

6. **Tải file**
   - Nếu xác thực thành công, click "Tải file đã giải mã"
   - File sẽ được lưu về máy

## 🔧 Cấu hình nâng cao

### File .env
```bash
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this-in-production

# Server Configuration
HOST=127.0.0.1
PORT=5000

# Database
DATABASE_URL=sqlite:///secure_transfer.db

# File Upload
MAX_CONTENT_LENGTH=16777216  # 16MB
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=txt,pdf,png,jpg,jpeg,gif,doc,docx,json,xml

# Security
RSA_KEY_SIZE=2048
SESSION_TIMEOUT=3600  # 1 hour
```

### Cấu trúc thư mục
```
secure-file-transfer/
├── server/               # Backend code
│   ├── app.py           # Flask application
│   ├── crypto_utils.py  # Encryption/decryption
│   ├── key_manager.py   # RSA key management
│   ├── file_handler.py  # File operations
│   └── socket_events.py # WebSocket handlers
├── client/              # Frontend code
│   ├── static/          # CSS, JavaScript
│   └── templates/       # HTML templates
├── shared/              # Shared modules
├── uploads/             # Temporary file storage
├── keys/                # Key storage
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
├── run.py              # Entry point
└── README.md           # This file
```

## 🔒 Bảo mật

### Các biện pháp bảo mật
- **Khóa riêng tư không bao giờ được gửi lên server**
- **Mã hóa hybrid**: RSA cho khóa AES, AES cho file
- **Chữ ký số**: Đảm bảo file không bị giả mạo
- **Hash verification**: Kiểm tra tính toàn vẹn
- **HTTPS recommended**: Sử dụng SSL/TLS cho production

### Lưu ý quan trọng
- Bảo mật khóa riêng tư cẩn thận
- Không chia sẻ khóa riêng tư với bất kỳ ai
- Sử dụng HTTPS khi deploy production
- Định kỳ backup khóa quan trọng

## 🧪 Testing

### Chạy unit tests
```bash
pytest tests/
```

### Test thủ công
1. Mở 2 browser tab/window
2. Tab 1: Đăng nhập là Alice (sender)
3. Tab 2: Đăng nhập là Bob (receiver)
4. Gửi file từ Alice đến Bob
5. Kiểm tra xác thực và giải mã

### Test file bị thay đổi
1. Gửi file bình thường
2. Sửa database để thay đổi hash
3. Nhận và kiểm tra cảnh báo

## 🚀 Deployment

### Development
```bash
python run.py
```

### Production với Gunicorn
```bash
pip install gunicorn
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 run:app
```

### Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "run:app"]
```

Build và chạy:
```bash
docker build -t secure-file-transfer .
docker run -p 5000:5000 secure-file-transfer
```

### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🐛 Troubleshooting

### WebSocket không kết nối
- Kiểm tra firewall
- Đảm bảo port 5000 không bị chặn
- Kiểm tra console browser để xem lỗi

### Mã hóa/giải mã thất bại
- Kiểm tra format khóa PEM
- Đảm bảo khóa public/private đúng cặp
- Kiểm tra kích thước file không vượt quá giới hạn

### File upload thất bại
- Kiểm tra kích thước file (mặc định 16MB)
- Kiểm tra định dạng file được phép
- Đảm bảo thư mục uploads có quyền ghi

## 📝 API Documentation

### REST Endpoints
- `GET /` - Trang chủ
- `GET /sender` - Giao diện người gửi
- `GET /receiver` - Giao diện người nhận
- `POST /api/generate_keys` - Tạo cặp khóa RSA
- `GET /api/public_key/<user_id>` - Lấy khóa công khai
- `POST /api/upload` - Upload file
- `POST /api/encrypt_and_send` - Mã hóa và gửi file
- `POST /api/decrypt_file` - Giải mã file

### WebSocket Events
- `connect` - Kết nối với server
- `register_user` - Đăng ký người dùng
- `request_public_key` - Yêu cầu khóa công khai
- `send_file` - Gửi file đã mã hóa
- `download_file` - Tải file về
- `get_online_users` - Lấy danh sách online
- `get_transfer_history` - Lấy lịch sử transfer

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:
1. Fork repository
2. Tạo branch mới (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request
.

## 📞 Liên hệ

- Email: nguyentrungthanhdev@example.com

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [PyCryptodome](https://pycryptodome.readthedocs.io/)
- [Socket.IO](https://socket.io/)
- [JSEncrypt](http://travistidwell.com/jsencrypt/)

---
Made with ❤️ by [Your Name]
