#!/usr/bin/env python3
"""
Test script to diagnose chart generation issues
"""
import os
import sys

# Add the project root to path
project_root = r"C:\Users\saiki\OneDrive\Desktop\hackerr'\TheNZT_Open_Source"
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Test the graph generation directly
from src.ai.tools.graph_gen_tool import generate_graphs_with_retry

# Sample NVIDIA stock data from the user's request
nvidia_data = """
NVIDIA Stock Price Trend (September 2025)
Date	Open	High	Low	Close
Sep 26, 2025	178.17	179.77	174.93	178.19
Sep 25, 2025	174.48	180.26	173.13	177.69
Sep 24, 2025	179.77	179.78	175.40	176.97
Sep 23, 2025	181.97	182.42	176.21	178.43
Sep 22, 2025	175.30	184.55	174.71	183.61
Sep 19, 2025	175.77	178.08	175.18	176.67
Sep 18, 2025	173.98	177.10	172.96	176.24
Sep 17, 2025	172.64	173.20	168.41	170.29
Sep 16, 2025	177.00	177.50	174.38	174.88
Sep 15, 2025	175.67	178.85	174.51	177.75
"""

print("🧪 TESTING CHART GENERATION WITH NEW API KEY")
print("="*80)
print(f"📊 Input data: {len(nvidia_data)} characters")
print(f"🔑 API Key status: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")

if os.getenv('GEMINI_API_KEY'):
    print(f"🔐 API Key: {os.getenv('GEMINI_API_KEY')[:10]}...{os.getenv('GEMINI_API_KEY')[-10:]}")

print("\n🚀 Starting chart generation test...")

try:
    result = generate_graphs_with_retry(nvidia_data, max_retries=3)
    
    print(f"\n📊 RESULT: {result}")
    
    if result == "NO_CHART_GENERATED":
        print("❌ CHART GENERATION FAILED!")
    else:
        print("✅ CHART GENERATION SUCCESSFUL!")
        
        # Try to parse as JSON
        import json
        try:
            parsed = json.loads(result)
            print(f"📈 Generated {len(parsed.get('chart_collection', []))} charts")
        except:
            print("⚠️ Result is not valid JSON")
            
except Exception as e:
    print(f"💥 ERROR: {e}")
    import traceback
    print(traceback.format_exc())
    
print("="*80)
print("🏁 TEST COMPLETE")