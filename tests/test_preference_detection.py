"""
Test suite for the preference detection system
"""
import asyncio
import pytest
import sys
import os

# Add the project root directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.backend.utils.preference_detector import PreferenceDetector

class TestPreferenceDetector:
    """Test cases for the PreferenceDetector class"""
    
    @pytest.fixture
    def detector(self):
        """Create a PreferenceDetector instance for testing"""
        return PreferenceDetector()
    
    def test_visual_keywords_detection(self, detector):
        """Test detection of visual preference keywords"""
        visual_texts = [
            "Show me charts and graphs for this data",
            "I want to see visual representations",
            "Can you create a diagram for this?",
            "Display the data with plots and visualizations",
            "I prefer seeing charts over text"
        ]
        
        for text in visual_texts:
            visual_score, keywords = detector._calculate_keyword_score(text, detector.VISUAL_KEYWORDS)
            assert visual_score > 0, f"Should detect visual preference in: {text}"
            assert len(keywords) > 0, f"Should find keywords in: {text}"
    
    def test_text_keywords_detection(self, detector):
        """Test detection of text preference keywords"""
        text_texts = [
            "Please explain this in detail",
            "I want comprehensive text descriptions",
            "Give me a thorough breakdown of the analysis",
            "Describe this step by step with detailed explanations",
            "I prefer reading detailed text over visuals"
        ]
        
        for text in text_texts:
            text_score, keywords = detector._calculate_keyword_score(text, detector.TEXT_KEYWORDS)
            assert text_score > 0, f"Should detect text preference in: {text}"
            assert len(keywords) > 0, f"Should find keywords in: {text}"
    
    @pytest.mark.asyncio
    async def test_preference_detection_visual(self, detector):
        """Test overall preference detection for visual preferences"""
        visual_input = "I want to see charts and graphs for the stock data analysis"
        result = await detector.detect_preference(visual_input)
        
        assert result["preference"] in ["visual", "mixed"], "Should detect visual or mixed preference"
        assert result["confidence"] > 0, "Should have some confidence"
        assert isinstance(result["keywords"], list), "Keywords should be a list"
        assert "preference" in result, "Result should contain preference"
        assert "confidence" in result, "Result should contain confidence"
    
    @pytest.mark.asyncio
    async def test_preference_detection_text(self, detector):
        """Test overall preference detection for text preferences"""
        text_input = "Please provide a detailed explanation with comprehensive analysis"
        result = await detector.detect_preference(text_input)
        
        assert result["preference"] in ["text", "mixed"], "Should detect text or mixed preference"
        assert result["confidence"] > 0, "Should have some confidence"
        assert isinstance(result["keywords"], list), "Keywords should be a list"
    
    @pytest.mark.asyncio
    async def test_preference_detection_neutral(self, detector):
        """Test preference detection for neutral input"""
        neutral_input = "What is the weather today?"
        result = await detector.detect_preference(neutral_input)
        
        assert result["preference"] in ["visual", "text", "mixed"], "Should return valid preference"
        assert result["confidence"] >= 0, "Confidence should be non-negative"
    
    @pytest.mark.asyncio
    async def test_empty_input_handling(self, detector):
        """Test handling of empty or minimal input"""
        empty_inputs = ["", " ", "hi", "ok"]
        
        for empty_input in empty_inputs:
            result = await detector.detect_preference(empty_input)
            assert result is not None, "Should handle empty input gracefully"
            assert "preference" in result, "Should return preference even for empty input"
    
    def test_keyword_scoring_weights(self, detector):
        """Test that keyword scoring follows weight hierarchy"""
        # Primary keywords should score higher than secondary
        primary_text = "chart"
        secondary_text = "show"
        
        primary_score, _ = detector._calculate_keyword_score(primary_text, detector.VISUAL_KEYWORDS)
        secondary_score, _ = detector._calculate_keyword_score(secondary_text, detector.VISUAL_KEYWORDS)
        
        assert primary_score >= secondary_score, "Primary keywords should score higher or equal to secondary"
    
    @pytest.mark.asyncio
    async def test_batch_detection(self, detector):
        """Test multiple preference detections"""
        test_cases = [
            "Show me a graph",
            "Explain in detail", 
            "Create a chart please",
            "Give me text description",
            "I want visual data"
        ]
        
        results = []
        for case in test_cases:
            result = await detector.detect_preference(case)
            results.append(result)
        
        assert len(results) == len(test_cases), "Should process all test cases"
        for result in results:
            assert "preference" in result, "Each result should have preference"
            assert result["confidence"] >= 0, "Each result should have valid confidence"

# Integration test for the full system
class TestPreferenceDetectionIntegration:
    """Integration tests for the preference detection system"""
    
    @pytest.mark.asyncio
    async def test_realistic_user_scenarios(self):
        """Test realistic user input scenarios"""
        detector = PreferenceDetector()
        
        scenarios = [
            {
                "input": "I need a comprehensive analysis of Tesla's stock performance with detailed financial breakdowns and explanations",
                "expected_tendency": "text"
            },
            {
                "input": "Show me charts and graphs for Apple stock trends over the last year",
                "expected_tendency": "visual"
            },
            {
                "input": "Can you create visual dashboards with stock performance data?",
                "expected_tendency": "visual"
            },
            {
                "input": "Please provide step-by-step detailed explanations of the market analysis",
                "expected_tendency": "text"
            }
        ]
        
        for scenario in scenarios:
            result = await detector.detect_preference(scenario["input"])
            
            # Check if detection aligns with expected tendency (allowing for mixed results)
            detected = result["preference"]
            expected = scenario["expected_tendency"]
            
            assert detected in [expected, "mixed"], f"Input: '{scenario['input']}' - Expected {expected} or mixed, got {detected}"
            assert result["confidence"] > 0, f"Should have confidence for: {scenario['input']}"

if __name__ == "__main__":
    # Run basic tests
    async def run_basic_tests():
        detector = PreferenceDetector()
        
        print("Testing Preference Detection System")
        print("=" * 50)
        
        test_cases = [
            "I want to see charts and graphs",
            "Please explain this in detail",
            "Show me visual data representations", 
            "Give me comprehensive text analysis",
            "Create diagrams and plots",
            "Provide thorough descriptions"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            result = await detector.detect_preference(test_case)
            print(f"Test {i}: '{test_case}'")
            print(f"  Preference: {result['preference']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Keywords: {result['keywords']}")
            print("-" * 30)
        
        print("All tests completed successfully!")

    # Run the tests
    asyncio.run(run_basic_tests())