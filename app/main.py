from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.models.models import Base
from app.routers.auth_router import router as auth_router
from app.routers.video_router import router as video_router
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Video Upload Service",
    description="A FastAPI service for video upload with JWT authentication and MinIO storage",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup all application routes
app.include_router(auth_router)
app.include_router(video_router)


@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")
        print("Please ensure PostgreSQL is running and database is accessible")


@app.get("/")
async def root():
    return {
        "message": "Video Upload Service API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "video-upload-service"}


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    raise HTTPException(
        status_code=500,
        detail=f"Internal server error: {str(exc)}"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
