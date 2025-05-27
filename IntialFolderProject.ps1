# Chạy lệnh sau để tạo thư mục dự án
# Tạo cấu trúc thư mục cho project
New-Item -ItemType Directory -Path "secure-file-transfer"
Set-Location -Path "secure-file-transfer"

# Tạo thư mục server
New-Item -ItemType Directory -Path "server"
New-Item -ItemType File -Path "server/__init__.py"
New-Item -ItemType File -Path "server/app.py"
New-Item -ItemType File -Path "server/crypto_utils.py"
New-Item -ItemType File -Path "server/key_manager.py"
New-Item -ItemType File -Path "server/file_handler.py"
New-Item -ItemType File -Path "server/socket_events.py"
New-Item -ItemType File -Path "server/config.py"

# Tạo thư mục client
New-Item -ItemType Directory -Path "client/static/css"
New-Item -ItemType Directory -Path "client/static/js"
New-Item -ItemType Directory -Path "client/static/keys"
New-Item -ItemType Directory -Path "client/templates"
New-Item -ItemType File -Path "client/static/css/style.css"
New-Item -ItemType File -Path "client/static/js/crypto.js"
New-Item -ItemType File -Path "client/static/js/socket.js"
New-Item -ItemType File -Path "client/static/js/main.js"
New-Item -ItemType File -Path "client/templates/index.html"
New-Item -ItemType File -Path "client/templates/sender.html"
New-Item -ItemType File -Path "client/templates/receiver.html"

# Tạo thư mục shared
New-Item -ItemType Directory -Path "shared"
New-Item -ItemType File -Path "shared/__init__.py"
New-Item -ItemType File -Path "shared/models.py"
New-Item -ItemType File -Path "shared/constants.py"

# Tạo thư mục tests
New-Item -ItemType Directory -Path "tests"
New-Item -ItemType File -Path "tests/__init__.py"
New-Item -ItemType File -Path "tests/test_crypto.py"
New-Item -ItemType File -Path "tests/test_file_handler.py"

# Tạo thư mục uploads và keys
New-Item -ItemType Directory -Path "uploads"
New-Item -ItemType Directory -Path "keys/server"
New-Item -ItemType Directory -Path "keys/client"

# Tạo các file cấu hình
New-Item -ItemType File -Path "requirements.txt"
New-Item -ItemType File -Path ".env"
New-Item -ItemType File -Path ".gitignore"
New-Item -ItemType File -Path "README.md"
New-Item -ItemType File -Path "run.py"

Write-Host "Cấu trúc project đã được tạo thành công!"