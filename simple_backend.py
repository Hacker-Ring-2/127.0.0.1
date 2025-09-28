"""
Ultra-Simple Backend Server for Testing Frontend API calls
No complex dependencies - just basic HTTP server
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
        
        # Route handlers
        if path == '/health':
            response = {"status": "healthy", "message": "Simple backend is running"}
        elif path == '/get_user_info':
            response = {
                "id": "user123",
                "email": "test@example.com",
                "full_name": "Test User",
                "profile_picture": None
            }
        elif path == '/get_user_preferences':
            response = {
                "preference": "mixed",
                "confidence": 0.0,
                "message": "No preferences set yet"
            }
        elif path == '/':
            response = {"message": "TheNZT Simple Backend is running!", "status": "healthy"}
        else:
            response = {"error": "Not found"}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
        
        # Parse the path
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == '/update_personalization':
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                input_text = data.get('input_text', '').lower()
                
                # Simple preference detection
                if any(word in input_text for word in ["chart", "graph", "visual", "diagram", "plot"]):
                    preference = "visual"
                    confidence = 0.8
                elif any(word in input_text for word in ["text", "explain", "detail", "description"]):
                    preference = "text"
                    confidence = 0.8
                else:
                    preference = "mixed"
                    confidence = 0.5
                
                response = {
                    "preference": preference,
                    "confidence": confidence,
                    "message": "Preferences updated successfully"
                }
            except:
                response = {"error": "Invalid request data"}
        else:
            response = {"error": "Not found"}
        
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, APIHandler)
    
    print("🚀 TheNZT Simple Backend Server Started")
    print("📡 Server running at: http://localhost:8000")
    print("🔗 Health check: http://localhost:8000/health")
    print("👤 User info: http://localhost:8000/get_user_info")
    print("🎯 Preferences: http://localhost:8000/get_user_preferences")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.server_close()
    except Exception as e:
        print(f"❌ Server error: {e}")
        httpd.server_close()

if __name__ == "__main__":
    run_server()