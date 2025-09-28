"""
Simple Mock Backend Server for Testing Frontend API calls
This server provides the basic endpoints needed for the frontend to work
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="TheNZT Mock Backend", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock user data
mock_user = {
    "id": "user123",
    "email": "test@example.com",
    "full_name": "Test User",
    "profile_picture": None
}

# Mock preference data
mock_preferences = {
    "preference": "mixed",
    "confidence": 0.0,
    "message": "No preferences set yet"
}

class PreferenceRequest(BaseModel):
    input_text: str
    session_id: str = "test-session"
    message_id: str = "test-message"

@app.get("/")
async def root():
    return {"message": "TheNZT Mock Backend is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Mock backend is running"}

@app.get("/get_user_info")
async def get_user_info():
    """Mock endpoint that returns user information"""
    return mock_user

@app.get("/get_user_preferences")
async def get_user_preferences():
    """Mock endpoint that returns user preferences"""
    return mock_preferences

@app.post("/update_personalization")
async def update_personalization(request: PreferenceRequest):
    """Mock endpoint that simulates preference detection"""
    
    # Simple mock preference detection
    input_text = request.input_text.lower()
    
    if any(word in input_text for word in ["chart", "graph", "visual", "diagram", "plot"]):
        preference = "visual"
        confidence = 0.8
    elif any(word in input_text for word in ["text", "explain", "detail", "description"]):
        preference = "text"
        confidence = 0.8
    else:
        preference = "mixed"
        confidence = 0.5
    
    return {
        "preference": preference,
        "confidence": confidence,
        "message": "Mock preferences updated successfully"
    }

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    print("🚀 Starting TheNZT Mock Backend Server...")
    print("📡 Server will run at: http://localhost:8000")
    print("🔗 Health check: http://localhost:8000/health")
    print("👤 User info: http://localhost:8000/get_user_info")
    print("🎯 Preferences: http://localhost:8000/get_user_preferences")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    uvicorn.run(
        "mock_backend:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )