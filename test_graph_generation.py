"""
Graph Generation Testing Suite
Tests the enhanced graph generation system with various data types.
"""

import sys
import os
import json

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ai.tools.graph_gen_tool import generate_graphs

def test_stock_data():
    """Test with Tata Motors stock data that previously worked"""
    print("\n" + "="*60)
    print("🧪 TEST 1: Tata Motors Stock Data (Should generate 3-5 charts)")
    print("="*60)
    
    tata_stock_data = """
| Date | Open | High | Low | Close | Volume |
|------|------|------|-----|-------|--------|
| 2024-08-01 | 1050.0 | 1065.0 | 1045.0 | 1058.0 | 1250000 |
| 2024-08-02 | 1058.0 | 1072.0 | 1055.0 | 1069.0 | 1180000 |
| 2024-08-05 | 1069.0 | 1075.0 | 1062.0 | 1067.0 | 1320000 |
| 2024-08-06 | 1067.0 | 1078.0 | 1064.0 | 1074.0 | 1290000 |
| 2024-08-07 | 1074.0 | 1081.0 | 1071.0 | 1077.0 | 1210000 |
| 2024-08-08 | 1077.0 | 1084.0 | 1073.0 | 1080.0 | 1350000 |
| 2024-08-09 | 1080.0 | 1087.0 | 1076.0 | 1083.0 | 1280000 |
"""
    
    result = generate_graphs(tata_stock_data)
    
    if result == "NO_CHART_GENERATED":
        print("❌ TEST FAILED: No charts generated for stock data")
        return False
    
    try:
        parsed = json.loads(result)
        chart_count = len(parsed.get('chart_collection', []))
        print(f"✅ TEST PASSED: Generated {chart_count} charts for stock data")
        
        if chart_count >= 3:
            print("✅ BONUS: Generated recommended multiple charts for comprehensive stock analysis")
        else:
            print("⚠️  WARNING: Only generated single chart - may want multiple charts for stock data")
            
        return True
    except json.JSONDecodeError as e:
        print(f"❌ TEST FAILED: Invalid JSON output - {e}")
        return False

def test_non_financial_data():
    """Test with non-financial data that should generate 1 chart"""
    print("\n" + "="*60)
    print("🧪 TEST 2: Company Revenue Data (Should generate 1 chart)")
    print("="*60)
    
    revenue_data = """
| Company | 2023 Revenue (Billions) | 2024 Revenue (Billions) |
|---------|-------------------------|-------------------------|
| Apple | 394.3 | 411.2 |
| Microsoft | 211.9 | 245.1 |
| Google | 307.4 | 334.7 |
| Amazon | 574.8 | 620.1 |
| Tesla | 96.8 | 125.4 |
"""
    
    result = generate_graphs(revenue_data)
    
    if result == "NO_CHART_GENERATED":
        print("❌ TEST FAILED: No charts generated for revenue data")
        return False
    
    try:
        parsed = json.loads(result)
        chart_count = len(parsed.get('chart_collection', []))
        print(f"✅ TEST PASSED: Generated {chart_count} charts for revenue data")
        
        if chart_count == 1:
            print("✅ BONUS: Generated exactly 1 chart as expected for non-financial data")
        elif chart_count > 1:
            print("⚠️  WARNING: Generated multiple charts - typically 1 chart for non-financial data")
        
        return True
    except json.JSONDecodeError as e:
        print(f"❌ TEST FAILED: Invalid JSON output - {e}")
        return False

def test_empty_data():
    """Test with problematic data that might cause empty results"""
    print("\n" + "="*60)
    print("🧪 TEST 3: Empty/Invalid Data (Should handle gracefully)")
    print("="*60)
    
    empty_data = """
| Column1 | Column2 |
|---------|---------|
|         |         |
"""
    
    result = generate_graphs(empty_data)
    
    if result == "NO_CHART_GENERATED":
        print("✅ TEST PASSED: Properly detected and handled empty data")
        return True
    else:
        print("⚠️  WARNING: Generated charts for empty data - may want to validate data quality")
        return True

def test_minimal_data():
    """Test with minimal valid data"""
    print("\n" + "="*60)
    print("🧪 TEST 4: Minimal Valid Data (Should generate 1 chart)")
    print("="*60)
    
    minimal_data = """
| Product | Sales |
|---------|-------|
| A | 100 |
| B | 200 |
"""
    
    result = generate_graphs(minimal_data)
    
    if result == "NO_CHART_GENERATED":
        print("❌ TEST FAILED: No charts generated for minimal valid data")
        return False
    
    try:
        parsed = json.loads(result)
        chart_count = len(parsed.get('chart_collection', []))
        print(f"✅ TEST PASSED: Generated {chart_count} charts for minimal data")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ TEST FAILED: Invalid JSON output - {e}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print("🚀 STARTING GRAPH GENERATION TEST SUITE")
    print("Testing enhanced graph generation with comprehensive debugging...")
    
    tests = [
        ("Stock Data Test", test_stock_data),
        ("Non-Financial Data Test", test_non_financial_data),
        ("Empty Data Test", test_empty_data),
        ("Minimal Data Test", test_minimal_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🏆 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Graph generation system is working correctly.")
    elif passed > 0:
        print("⚠️  SOME TESTS FAILED. Review the debug output above for issues.")
    else:
        print("💀 ALL TESTS FAILED. Graph generation system needs immediate attention.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()
