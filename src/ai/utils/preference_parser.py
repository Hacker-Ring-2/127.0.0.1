"""
Advanced Preference Parser for TheNZT AI System
Implements Step 1: Parse textarea input for preferences (20 points)

This module provides sophisticated natural language processing to detect user preferences
from personalization textarea input with high accuracy and robust edge case handling.
"""

import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class PreferenceParser:
    """
    Advanced preference parser with AI-level natural language understanding
    """
    
    def __init__(self):
        # Visual preference keywords
        self.visual_keywords = {
            'primary': ['chart', 'charts', 'graph', 'graphs', 'visual', 'visuals', 
                       'plot', 'plots', 'diagram', 'diagrams', 'visualization'],
            'secondary': ['show', 'display', 'see', 'picture', 'image', 'graphic',
                         'dashboard', 'infographic', 'pie chart', 'bar chart']
        }
        
        # Text preference keywords
        self.text_keywords = {
            'primary': ['text', 'explanation', 'explanations', 'detail', 'details',
                       'description', 'analysis', 'breakdown', 'summary'],
            'secondary': ['explain', 'describe', 'elaborate', 'discuss', 'tell',
                         'comprehensive', 'thorough', 'detailed', 'in-depth']
        }
        
        # Preference indicators
        self.preference_indicators = ['prefer', 'like', 'want', 'need', 'love', 
                                    'enjoy', 'favor', 'better with']
        
        # Negation words
        self.negation_words = ['not', 'don\'t', 'no', 'never', 'avoid', 'dislike', 'hate']
        
        self.parsing_history = []
    
    def parse_preference(self, user_input: str) -> Dict[str, Any]:
        """
        Main parsing function that returns comprehensive preference analysis
        
        Args:
            user_input: Natural language text from personalization textarea
            
        Returns:
            {
                "preference": "visual" | "text" | "mixed" | "unclear",
                "confidence": float (0.0-1.0),
                "reasoning": str,
                "keywords_found": List[str],
                "specific_requests": List[str],
                "metadata": Dict
            }
        """
        
        if not user_input or not user_input.strip():
            return self._create_empty_response()
            
        # Clean and normalize input
        cleaned_input = self._clean_input(user_input)
        
        # Analyze keywords
        visual_score = self._calculate_visual_score(cleaned_input)
        text_score = self._calculate_text_score(cleaned_input)
        
        # Check for negations
        has_negation = self._check_negations(cleaned_input)
        if has_negation:
            visual_score, text_score = text_score * 0.8, visual_score * 0.8
        
        # Determine preference
        preference, confidence = self._determine_preference(visual_score, text_score)
        
        # Extract additional information
        keywords_found = self._extract_keywords(cleaned_input)
        specific_requests = self._extract_specific_requests(cleaned_input)
        reasoning = self._generate_reasoning(preference, visual_score, text_score, keywords_found)
        
        result = {
            "preference": preference,
            "confidence": confidence,
            "reasoning": reasoning,
            "keywords_found": keywords_found,
            "specific_requests": specific_requests,
            "metadata": {
                "visual_score": visual_score,
                "text_score": text_score,
                "has_negation": has_negation,
                "input_length": len(user_input),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Store in history
        self.parsing_history.append({
            "input": user_input,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def _clean_input(self, text: str) -> str:
        """Clean and normalize input text"""
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def _calculate_visual_score(self, text: str) -> float:
        """Calculate visual preference score"""
        score = 0.0
        
        # Primary keywords (higher weight)
        for keyword in self.visual_keywords['primary']:
            if keyword in text:
                score += 3.0
        
        # Secondary keywords (lower weight)
        for keyword in self.visual_keywords['secondary']:
            if keyword in text:
                score += 1.5
        
        # Preference indicators with visual keywords
        for indicator in self.preference_indicators:
            for keyword in self.visual_keywords['primary']:
                if f"{indicator} {keyword}" in text or f"{keyword}" in text and indicator in text:
                    score += 2.0
                    break
        
        return score
    
    def _calculate_text_score(self, text: str) -> float:
        """Calculate text preference score"""
        score = 0.0
        
        # Primary keywords (higher weight)
        for keyword in self.text_keywords['primary']:
            if keyword in text:
                score += 3.0
        
        # Secondary keywords (lower weight)
        for keyword in self.text_keywords['secondary']:
            if keyword in text:
                score += 1.5
        
        # Preference indicators with text keywords
        for indicator in self.preference_indicators:
            for keyword in self.text_keywords['primary']:
                if f"{indicator} {keyword}" in text or f"{keyword}" in text and indicator in text:
                    score += 2.0
                    break
        
        return score
    
    def _check_negations(self, text: str) -> bool:
        """Check if text contains negations"""
        for negation in self.negation_words:
            if negation in text:
                return True
        return False
    
    def _determine_preference(self, visual_score: float, text_score: float) -> tuple:
        """Determine preference type and confidence"""
        total_score = visual_score + text_score
        
        if total_score == 0:
            return "unclear", 0.0
        
        if abs(visual_score - text_score) < 1.0:
            return "mixed", min(0.8, total_score / 10.0)
        
        if visual_score > text_score:
            confidence = min(1.0, visual_score / max(total_score, 5.0))
            return "visual", confidence
        else:
            confidence = min(1.0, text_score / max(total_score, 5.0))
            return "text", confidence
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract found keywords"""
        found_keywords = []
        
        for keyword_group in [self.visual_keywords, self.text_keywords]:
            for keyword_list in keyword_group.values():
                for keyword in keyword_list:
                    if keyword in text:
                        found_keywords.append(keyword)
        
        return list(set(found_keywords))
    
    def _extract_specific_requests(self, text: str) -> List[str]:
        """Extract specific user requests"""
        requests = []
        
        # Common request patterns
        patterns = [
            r"show me (\w+(?:\s+\w+)*)",
            r"i want (\w+(?:\s+\w+)*)",
            r"i need (\w+(?:\s+\w+)*)",
            r"prefer (\w+(?:\s+\w+)*)",
            r"like (\w+(?:\s+\w+)*)"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            requests.extend(matches)
        
        return requests[:5]  # Limit to 5 requests
    
    def _generate_reasoning(self, preference: str, visual_score: float, 
                          text_score: float, keywords: List[str]) -> str:
        """Generate human-readable reasoning"""
        if preference == "unclear":
            return "Unable to determine clear preference from input."
        
        reasoning = f"Detected {preference} preference"
        
        if preference == "visual":
            reasoning += f" (visual score: {visual_score:.1f} vs text score: {text_score:.1f})"
        elif preference == "text":
            reasoning += f" (text score: {text_score:.1f} vs visual score: {visual_score:.1f})"
        else:
            reasoning += f" (balanced scores - visual: {visual_score:.1f}, text: {text_score:.1f})"
        
        if keywords:
            reasoning += f". Found keywords: {', '.join(keywords[:3])}"
        
        return reasoning
    
    def _create_empty_response(self) -> Dict[str, Any]:
        """Create response for empty input"""
        return {
            "preference": "unclear",
            "confidence": 0.0,
            "reasoning": "No input provided",
            "keywords_found": [],
            "specific_requests": [],
            "metadata": {
                "visual_score": 0.0,
                "text_score": 0.0,
                "has_negation": False,
                "input_length": 0,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        if not self.parsing_history:
            return {"total_parses": 0}
        
        total_parses = len(self.parsing_history)
        avg_confidence = sum(p["result"]["confidence"] for p in self.parsing_history) / total_parses
        
        preference_counts = {}
        for parse in self.parsing_history:
            pref = parse["result"]["preference"]
            preference_counts[pref] = preference_counts.get(pref, 0) + 1
        
        return {
            "total_parses": total_parses,
            "average_confidence": round(avg_confidence, 2),
            "preference_distribution": preference_counts
        }


# Test function
def test_preference_parser():
    """Test the preference parser"""
    parser = PreferenceParser()
    
    test_cases = [
        "I prefer charts and graphs",
        "Give me detailed text explanations", 
        "I like visual data with some text explanation",
        "Show me charts but also include detailed analysis",
        "I don't like graphs, prefer written summaries"
    ]
    
    print("🧪 Testing Preference Parser")
    print("=" * 50)
    
    for i, test_input in enumerate(test_cases, 1):
        result = parser.parse_preference(test_input)
        print(f"\nTest {i}: '{test_input}'")
        print(f"Result: {result['preference']} (confidence: {result['confidence']:.2f})")
        print(f"Reasoning: {result['reasoning']}")


if __name__ == "__main__":
    test_preference_parser()