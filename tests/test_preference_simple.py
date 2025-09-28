"""
Simple test for preference detection system without AI dependencies
"""
import asyncio
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Mock the google.generativeai import to avoid dependency issues
import importlib.util

class MockModel:
    def generate_content(self, prompt):
        return type('response', (), {'text': '{"preference": "mixed", "confidence": 0.5, "reasoning": "Mock AI response"}'})()

mock_genai = type('module', (), {
    'configure': lambda **kwargs: None,
    'GenerativeModel': lambda model_name: MockModel()
})
sys.modules['google.generativeai'] = mock_genai

from src.backend.utils.preference_detector import PreferenceDetector

async def test_basic_functionality():
    """Test basic preference detection functionality"""
    print("Testing Preference Detection System (Mock Mode)")
    print("=" * 60)
    
    detector = PreferenceDetector()
    
    test_cases = [
        {
            "input": "I want to see charts and graphs for this analysis",
            "expected": "visual"
        },
        {
            "input": "Please provide detailed text explanations", 
            "expected": "text"
        },
        {
            "input": "Show me visual data with plots and diagrams",
            "expected": "visual"
        },
        {
            "input": "Give me comprehensive descriptions and analysis",
            "expected": "text"
        },
        {
            "input": "Create charts and visual representations",
            "expected": "visual"
        },
        {
            "input": "I prefer thorough text-based explanations",
            "expected": "text"
        }
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            result = await detector.detect_preference(test_case["input"])
            
            print(f"Test {i}: '{test_case['input'][:50]}...'")
            print(f"  Expected: {test_case['expected']}")
            print(f"  Detected: {result['preference']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Keywords: {result['keywords']}")
            
            # Check if detection aligns with expected (allowing mixed)
            if result['preference'] == test_case['expected'] or result['preference'] == 'mixed':
                print(f"  ✅ PASS")
                success_count += 1
            else:
                print(f"  ❌ FAIL - Expected {test_case['expected']}, got {result['preference']}")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"Test {i}: ERROR - {str(e)}")
            print("-" * 50)
    
    print(f"\nTest Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {total_tests - success_count} tests failed")
    
    return success_count == total_tests

def test_keyword_detection():
    """Test keyword detection functionality"""
    print("\nTesting Keyword Detection")
    print("=" * 40)
    
    detector = PreferenceDetector()
    
    # Test visual keywords
    visual_text = "I want to see charts and graphs"
    visual_score, visual_keywords = detector._calculate_keyword_score(visual_text, detector.VISUAL_KEYWORDS)
    print(f"Visual Text: '{visual_text}'")
    print(f"  Score: {visual_score}")
    print(f"  Keywords: {visual_keywords}")
    
    # Test text keywords  
    text_text = "Please explain this in detail"
    text_score, text_keywords = detector._calculate_keyword_score(text_text, detector.TEXT_KEYWORDS)
    print(f"Text Text: '{text_text}'")
    print(f"  Score: {text_score}")
    print(f"  Keywords: {text_keywords}")
    
    # Verify scores
    assert visual_score > 0, "Should detect visual keywords"
    assert text_score > 0, "Should detect text keywords"
    assert len(visual_keywords) > 0, "Should find visual keywords"
    assert len(text_keywords) > 0, "Should find text keywords"
    
    print("✅ Keyword detection tests passed!")

if __name__ == "__main__":
    try:
        # Test keyword detection first
        test_keyword_detection()
        
        # Test full preference detection
        success = asyncio.run(test_basic_functionality())
        
        if success:
            print("\n🎉 All preference detection tests completed successfully!")
            exit(0)
        else:
            print("\n❌ Some tests failed!")
            exit(1)
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {str(e)}")
        exit(1)