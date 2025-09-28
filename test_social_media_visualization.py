#!/usr/bin/env python3
"""
Test script to verify social media visualization capabilities
"""

import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.ai.tools.graph_gen_tool import graph_generation_tool
from src.ai.tools.web_search_tools import advanced_internet_search

async def test_social_media_visualization():
    """Test the social media visualization system"""
    
    print("🧪 Testing Social Media Visualization System")
    print("=" * 50)
    
    # Test 1: Graph Generation Tool with Social Media Data
    print("\n📊 Test 1: Graph Generation Tool")
    print("-" * 30)
    
    # Sample social media data table
    social_media_data = """
| Platform | Monthly Active Users (Billions) | Revenue 2024 (Billions USD) | User Growth Rate (%) |
|----------|----------------------------------|------------------------------|---------------------|
| Facebook | 3.07 | 134.9 | 3.2 |
| YouTube | 2.70 | 31.5 | 5.1 |
| Instagram | 2.35 | 47.4 | 7.3 |
| TikTok | 1.67 | 18.2 | 12.8 |
| LinkedIn | 0.93 | 15.7 | 8.4 |
| Twitter/X | 0.54 | 5.1 | -2.1 |
"""
    
    print(f"Input data:\n{social_media_data}")
    
    try:
        result = graph_generation_tool._run(social_media_data)
        print(f"\n✅ Graph Generation Result:\n{result}")
        
        if result != "NO_CHART_GENERATED":
            print("✅ Graph generation successful!")
        else:
            print("❌ Graph generation failed!")
            
    except Exception as e:
        print(f"❌ Graph generation error: {e}")
    
    # Test 2: Web Search for Social Media Statistics
    print("\n\n🔍 Test 2: Web Search for Social Media Data")
    print("-" * 40)
    
    try:
        search_result = await advanced_internet_search("social media platform user statistics 2024 active users")
        print(f"✅ Search completed. Found {len(search_result)} characters of data")
        print(f"Sample content: {search_result[:200]}...")
        
    except Exception as e:
        print(f"❌ Search error: {e}")
    
    # Test 3: Combined Test - Search + Visualize
    print("\n\n🎯 Test 3: Complete Visualization Workflow")
    print("-" * 40)
    
    try:
        # Search for real data
        search_query = "social media engagement statistics 2024 platform comparison"
        search_data = await advanced_internet_search(search_query)
        print(f"✅ Search completed for: {search_query}")
        
        # Create a test table from typical social media metrics
        test_table = """
| Metric | Facebook | Instagram | TikTok | YouTube |
|--------|----------|-----------|--------|---------|
| Daily Active Users (Millions) | 2100 | 1500 | 1200 | 2000 |
| Average Session Time (Minutes) | 33 | 53 | 95 | 74 |
| Engagement Rate (%) | 6.2 | 4.7 | 17.5 | 3.1 |
| Ad Revenue per User ($) | 41.2 | 20.1 | 10.9 | 15.7 |
"""
        
        chart_result = graph_generation_tool._run(test_table)
        
        if chart_result != "NO_CHART_GENERATED":
            print("✅ Complete workflow successful!")
            print(f"Generated chart: {chart_result[:100]}...")
        else:
            print("❌ Visualization failed in complete workflow")
            
    except Exception as e:
        print(f"❌ Complete workflow error: {e}")

if __name__ == "__main__":
    asyncio.run(test_social_media_visualization())
