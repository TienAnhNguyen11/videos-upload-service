# Video Upload Service

Một backend service được xây dựng bằng FastAPI để upload video với JWT authentication và MinIO storage, được thiết kế theo hướng OOP cho service layer và functional cho router layer.

## Tính năng

- **JWT Authentication**: Xác thực người dùng bằng JWT tokens
- **Pre-signed URL Upload**: Client upload trực tiếp lên MinIO thông qua pre-signed URL
- **PostgreSQL Database**: Lưu trữ metadata video và thông tin người dùng
- **MinIO Storage**: Lưu trữ file video
- **OOP Service Layer**: Service layer được thiết kế theo hướng Object-Oriented Programming
- **Functional Router Layer**: Router layer sử dụng functional programming approach

## Cấu trúc Project

```
videos-upload-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── crud.py                 # Deprecated - use services instead
│   ├── core/                   # Core configuration & database
│   │   ├── __init__.py
│   │   ├── config.py           # Application settings
│   │   └── database.py         # Database connection
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   └── models.py           # SQLAlchemy models
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py          # Request/Response schemas
│   ├── services/               # Service layer (OOP)
│   │   ├── __init__.py
│   │   ├── base_service.py     # Base service class
│   │   ├── user_service.py     # User operations
│   │   ├── video_service.py    # Video operations
│   │   ├── auth_service.py     # Authentication operations
│   │   └── minio_service.py    # MinIO operations
│   ├── routers/                # API routes (Functional)
│   │   ├── __init__.py
│   │   ├── auth_router.py      # Authentication endpoints
│   │   └── video_router.py     # Video endpoints
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── auth.py             # Authentication utilities
│       └── password.py         # Password hashing utilities
├── alembic/                    # Database migrations
│   ├── env.py
│   └── script.py.mako
├── scripts/                    # Utility scripts
│   └── init_db.py             # Database initialization
├── requirements.txt            # Python dependencies
├── env.example                 # Environment variables template
├── alembic.ini                 # Alembic configuration
└── README.md                   # This file
```

## Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd videos-upload-service
```

### 2. Tạo virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường
```bash
cp env.example .env
```

Chỉnh sửa file `.env` với thông tin của bạn:
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/video_upload_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# MinIO
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET_NAME=video-uploads
MINIO_SECURE=false

# App
APP_HOST=0.0.0.0
APP_PORT=8000
```

### 5. Thiết lập database
```bash
# Tạo database PostgreSQL
createdb video_upload_db

# Chạy migrations
alembic upgrade head
```

### 6. Khởi động MinIO
```bash
# Sử dụng Docker
docker run -p 9000:9000 -p 9001:9001 \
  -e "MINIO_ROOT_USER=your-access-key" \
  -e "MINIO_ROOT_PASSWORD=your-secret-key" \
  minio/minio server /data --console-address ":9001"
```

### 7. Chạy ứng dụng
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication
- `POST /auth/register` - Đăng ký người dùng mới
- `POST /auth/token` - Đăng nhập và lấy access token
- `POST /auth/refresh` - Refresh access token
- `GET /auth/me` - Lấy thông tin người dùng hiện tại

### Video Upload Flow
1. `POST /videos/upload?filename=video.mp4` - Lấy pre-signed URL để upload
2. Client upload file trực tiếp lên MinIO sử dụng pre-signed URL
3. `POST /videos/{video_id}/metadata` - Cập nhật metadata sau khi upload thành công

### Video Management
- `GET /videos/` - Lấy danh sách video của user
- `GET /videos/{video_id}` - Lấy thông tin video cụ thể
- `PUT /videos/{video_id}` - Cập nhật thông tin video
- `DELETE /videos/{video_id}` - Xóa video

## Architecture Design

### Service Layer (OOP)
- **BaseService**: Abstract base class cho tất cả services
- **UserService**: Xử lý operations liên quan đến User
- **VideoService**: Xử lý operations liên quan đến Video
- **AuthService**: Xử lý authentication và authorization
- **MinioService**: Xử lý tương tác với MinIO storage

### Router Layer (Functional)
- **auth_router.py**: Authentication endpoints sử dụng functional approach
- **video_router.py**: Video endpoints sử dụng functional approach

### Benefits của Hybrid Design
- **Service Layer OOP**: 
  - Encapsulation: Logic business được đóng gói trong service classes
  - Inheritance: Tái sử dụng code thông qua BaseService
  - Polymorphism: Có thể dễ dàng thay thế implementations
  - Maintainability: Code dễ bảo trì và mở rộng
  - Testability: Dễ dàng viết unit tests

- **Router Layer Functional**:
  - Simplicity: Code đơn giản, dễ đọc và hiểu
  - Performance: Ít overhead hơn so với OOP
  - FastAPI Native: Tận dụng tốt FastAPI's dependency injection
  - Flexibility: Dễ dàng thêm/sửa/xóa endpoints

## Ví dụ sử dụng

### 1. Đăng ký người dùng
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. Đăng nhập
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

### 3. Upload video
```bash
# Bước 1: Lấy pre-signed URL
curl -X POST "http://localhost:8000/videos/upload?filename=video.mp4" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Bước 2: Upload file lên MinIO (sử dụng pre-signed URL từ response)

# Bước 3: Cập nhật metadata
curl -X POST "http://localhost:8000/videos/1/metadata" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Video",
    "description": "A great video",
    "tags": ["fun", "entertainment"]
  }'
```

## Development

### Tạo migration mới
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Chạy tests (nếu có)
```bash
pytest
```

### Code formatting
```bash
black app/
isort app/
```

## Production Deployment

1. **Environment Variables**: Cấu hình đầy đủ các biến môi trường
2. **Database**: Sử dụng PostgreSQL production database
3. **MinIO**: Cấu hình MinIO cluster cho production
4. **Security**: Cấu hình CORS, rate limiting, và security headers
5. **Monitoring**: Thêm logging và monitoring
6. **SSL/TLS**: Cấu hình HTTPS

## Contributing

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## License

MIT License