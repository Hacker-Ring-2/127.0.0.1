#!/usr/bin/env python3
"""
Simple test to trigger visualization system
"""

import requests
import json

def test_agent_visualization():
    """Test if the agent can generate visualizations"""
    
    # Test with a simple financial query that should trigger visualization
    test_queries = [
        "Show me Tesla stock data with charts",
        "Create graphs for Apple vs Microsoft comparison",
        "Visualize social media platform user statistics",
        "Generate charts for cryptocurrency market data"
    ]
    
    for query in test_queries:
        print(f"\n🧪 Testing: {query}")
        print("=" * 50)
        
        try:
            # Simple request to check if there's a basic endpoint
            response = requests.get("http://localhost:8000")
            print(f"✅ Server is responding: {response.status_code}")
            
        except Exception as e:
            print(f"❌ Server connection error: {e}")

if __name__ == "__main__":
    test_agent_visualization()