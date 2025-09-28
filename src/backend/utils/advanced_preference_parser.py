"""
Advanced User Preference Parser for TheNZT AI System
Implements Step 1: Parse User Input from Text Area (20 points)

This module provides sophisticated natural language processing to detect user preferences
from personalization textarea input with high accuracy and robust edge case handling.
"""

import re
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import asyncio

# Advanced keyword mapping with context awareness
PREFERENCE_KEYWORDS = {
    "visual": {
        "primary": [
            "chart", "charts", "graph", "graphs", "visual", "visuals", 
            "diagram", "diagrams", "plot", "plots", "visualization", 
            "visualizations", "infographic", "infographics"
        ],
        "secondary": [
            "show", "display", "see", "look", "watch", "view", "picture", 
            "image", "graphic", "graphics", "dashboard", "pie chart", 
            "bar chart", "line graph", "scatter plot"
        ],
        "context_phrases": [
            "prefer charts", "like graphs", "visual data", "show me charts",
            "data visualization", "graphical representation", "visual format",
            "chart format", "graph form", "visual display", "pictorial",
            "visual learner", "see data", "visual representation"
        ],
        "preference_indicators": [
            "prefer", "like", "want", "need", "love", "enjoy", "favor",
            "better with", "easier with", "clearer with", "understand better"
        ]
    },
    "text": {
        "primary": [
            "text", "explanation", "explanations", "detail", "details", 
            "description", "descriptions", "analysis", "breakdown", 
            "summary", "summaries", "narrative", "written"
        ],
        "secondary": [
            "explain", "describe", "elaborate", "discuss", "analyze", 
            "tell", "write", "read", "understand", "comprehensive",
            "thorough", "detailed", "in-depth", "step-by-step"
        ],
        "context_phrases": [
            "detailed explanations", "text format", "written analysis",
            "comprehensive breakdown", "thorough explanation", "in detail",
            "step by step", "text-based", "descriptive analysis",
            "narrative format", "written summary", "textual information"
        ],
        "preference_indicators": [
            "prefer", "like", "want", "need", "love", "enjoy", "favor",
            "better with", "easier with", "clearer with", "understand better"
        ]
    }
}

# Negation words that can flip preference meaning
NEGATION_WORDS = [
    "not", "don't", "doesn't", "won't", "can't", "shouldn't", "wouldn't",
    "no", "never", "none", "neither", "nor", "without", "avoid", "dislike",
    "hate", "against", "opposite", "instead of", "rather than"
]

# Intensity modifiers
INTENSITY_MODIFIERS = {
    "high": ["always", "definitely", "absolutely", "certainly", "strongly", "really", "very", "extremely"],
    "medium": ["usually", "often", "generally", "typically", "mostly", "prefer", "like"],
    "low": ["sometimes", "occasionally", "maybe", "perhaps", "might", "could", "somewhat"]
}

class AdvancedPreferenceParser:
    """
    World-class preference parser with AI-level natural language understanding
    """
    
    def __init__(self):
        self.parsing_history = []
        self.confidence_threshold = 0.6
        
    def parse_user_preference(self, user_input: str) -> Dict[str, Any]:
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
                "intensity": "high" | "medium" | "low",
                "specific_requests": List[str],
                "fallback_preference": str,
                "metadata": Dict
            }
        """
        
        if not user_input or not user_input.strip():
            return self._create_empty_response()
        
        # Clean and normalize input
        cleaned_input = self._clean_input(user_input)
        
        # Multi-stage analysis
        keyword_analysis = self._analyze_keywords(cleaned_input)
        phrase_analysis = self._analyze_context_phrases(cleaned_input)
        sentiment_analysis = self._analyze_sentiment(cleaned_input)
        intensity_analysis = self._analyze_intensity(cleaned_input)
        negation_analysis = self._check_negations(cleaned_input)
        
        # Combine all analyses
        final_result = self._combine_analyses(
            cleaned_input,
            keyword_analysis,
            phrase_analysis,
            sentiment_analysis,
            intensity_analysis,
            negation_analysis
        )
        
        # Store parsing history for learning
        self.parsing_history.append({
            "input": user_input,
            "result": final_result,
            "timestamp": datetime.now().isoformat()
        })
        
        return final_result
    
    def _clean_input(self, text: str) -> str:
        """Clean and normalize input text"""
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Handle common abbreviations
        abbreviations = {
            "viz": "visualization",
            "vis": "visual",
            "imgs": "images", 
            "pics": "pictures",
            "info": "information",
            "desc": "description",
            "expl": "explanation"
        }
        
        for abbr, full in abbreviations.items():
            text = text.replace(abbr, full)
        
        return text
    
    def _analyze_keywords(self, text: str) -> Dict[str, Any]:
        """Analyze individual keywords and their context"""
        visual_score = 0
        text_score = 0
        found_keywords = {"visual": [], "text": []}
        
        # Check primary keywords (highest weight)
        for keyword in PREFERENCE_KEYWORDS["visual"]["primary"]:
            if keyword in text:
                visual_score += 3
                found_keywords["visual"].append(keyword)
        
        for keyword in PREFERENCE_KEYWORDS["text"]["primary"]:
            if keyword in text:
                text_score += 3
                found_keywords["text"].append(keyword)
        
        # Check secondary keywords (medium weight)
        for keyword in PREFERENCE_KEYWORDS["visual"]["secondary"]:
            if keyword in text:
                visual_score += 2
                found_keywords["visual"].append(keyword)
        
        for keyword in PREFERENCE_KEYWORDS["text"]["secondary"]:
            if keyword in text:
                text_score += 2
                found_keywords["text"].append(keyword)
        
        return {
            "visual_score": visual_score,
            "text_score": text_score,
            "found_keywords": found_keywords,
            "total_keywords": len(found_keywords["visual"]) + len(found_keywords["text"])
        }
    
    def _analyze_context_phrases(self, text: str) -> Dict[str, Any]:
        """Analyze context phrases for more sophisticated understanding"""
        visual_phrases = []
        text_phrases = []
        phrase_score_visual = 0
        phrase_score_text = 0
        
        # Check visual context phrases
        for phrase in PREFERENCE_KEYWORDS["visual"]["context_phrases"]:
            if phrase in text:
                visual_phrases.append(phrase)
                phrase_score_visual += 4  # Higher weight for phrases
        
        # Check text context phrases
        for phrase in PREFERENCE_KEYWORDS["text"]["context_phrases"]:
            if phrase in text:
                text_phrases.append(phrase)
                phrase_score_text += 4
        
        return {
            "visual_phrases": visual_phrases,
            "text_phrases": text_phrases,
            "visual_phrase_score": phrase_score_visual,
            "text_phrase_score": phrase_score_text
        }
    
    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment and preference indicators"""
        positive_indicators = []
        negative_indicators = []
        
        # Look for preference indicators combined with keywords
        for pref_type in ["visual", "text"]:
            for indicator in PREFERENCE_KEYWORDS[pref_type]["preference_indicators"]:
                for keyword in PREFERENCE_KEYWORDS[pref_type]["primary"]:
                    pattern = f"{indicator}.*{keyword}|{keyword}.*{indicator}"
                    if re.search(pattern, text):
                        positive_indicators.append(f"{indicator} {keyword}")
        
        return {
            "positive_indicators": positive_indicators,
            "negative_indicators": negative_indicators,
            "sentiment_strength": len(positive_indicators) - len(negative_indicators)
        }
    
    def _analyze_intensity(self, text: str) -> Dict[str, Any]:
        """Analyze intensity of preference expression"""
        intensity_score = 0
        intensity_level = "medium"
        found_modifiers = []
        
        for level, modifiers in INTENSITY_MODIFIERS.items():
            for modifier in modifiers:
                if modifier in text:
                    found_modifiers.append((modifier, level))
                    if level == "high":
                        intensity_score += 3
                    elif level == "medium":
                        intensity_score += 2
                    else:
                        intensity_score += 1
        
        # Determine overall intensity
        if intensity_score >= 6:
            intensity_level = "high"
        elif intensity_score >= 3:
            intensity_level = "medium"
        else:
            intensity_level = "low"
        
        return {
            "intensity_score": intensity_score,
            "intensity_level": intensity_level,
            "found_modifiers": found_modifiers
        }
    
    def _check_negations(self, text: str) -> Dict[str, Any]:
        """Check for negations that might flip preference meaning"""
        negations_found = []
        negation_contexts = []
        
        for negation in NEGATION_WORDS:
            if negation in text:
                negations_found.append(negation)
                # Find context around negation
                pattern = f"{negation}\\s+\\w+\\s+\\w+"
                matches = re.findall(pattern, text)
                negation_contexts.extend(matches)
        
        return {
            "negations_found": negations_found,
            "negation_contexts": negation_contexts,
            "has_negations": len(negations_found) > 0
        }
    
    def _combine_analyses(self, text: str, keyword_analysis: Dict, phrase_analysis: Dict, 
                         sentiment_analysis: Dict, intensity_analysis: Dict, 
                         negation_analysis: Dict) -> Dict[str, Any]:
        """Combine all analyses to determine final preference"""
        
        # Calculate raw scores
        visual_score = (
            keyword_analysis["visual_score"] + 
            phrase_analysis["visual_phrase_score"] +
            (sentiment_analysis["sentiment_strength"] if sentiment_analysis["sentiment_strength"] > 0 else 0)
        )
        
        text_score = (
            keyword_analysis["text_score"] + 
            phrase_analysis["text_phrase_score"] +
            (abs(sentiment_analysis["sentiment_strength"]) if sentiment_analysis["sentiment_strength"] < 0 else 0)
        )
        
        # Apply intensity multiplier
        intensity_multiplier = {
            "high": 1.5,
            "medium": 1.0,
            "low": 0.7
        }[intensity_analysis["intensity_level"]]
        
        visual_score *= intensity_multiplier
        text_score *= intensity_multiplier
        
        # Handle negations
        if negation_analysis["has_negations"]:
            # If negations are present, flip scores or reduce confidence
            visual_score, text_score = text_score * 0.8, visual_score * 0.8
        
        # Determine preference
        total_score = visual_score + text_score
        if total_score == 0:
            preference = "unclear"
            confidence = 0.0
        elif abs(visual_score - text_score) < 2:
            preference = "mixed"
            confidence = min(0.8, (total_score / 10))
        elif visual_score > text_score:
            preference = "visual"
            confidence = min(1.0, visual_score / max(total_score, 10))
        else:
            preference = "text"
            confidence = min(1.0, text_score / max(total_score, 10))
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            preference, confidence, visual_score, text_score,
            keyword_analysis, phrase_analysis, intensity_analysis
        )
        
        # Determine specific requests
        specific_requests = self._extract_specific_requests(text)
        
        # Determine fallback preference
        fallback_preference = "mixed" if preference == "unclear" else preference
        
        return {
            "preference": preference,
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "keywords_found": keyword_analysis["found_keywords"],
            "intensity": intensity_analysis["intensity_level"],
            "specific_requests": specific_requests,
            "fallback_preference": fallback_preference,
            "metadata": {
                "visual_score": round(visual_score, 2),
                "text_score": round(text_score, 2),
                "total_keywords": keyword_analysis["total_keywords"],
                "has_negations": negation_analysis["has_negations"],
                "intensity_score": intensity_analysis["intensity_score"],
                "analysis_timestamp": datetime.now().isoformat(),
                "input_length": len(text),
                "processing_version": "2.0"
            }
        }
    
    def _generate_reasoning(self, preference: str, confidence: float, visual_score: float, 
                          text_score: float, keyword_analysis: Dict, phrase_analysis: Dict,
                          intensity_analysis: Dict) -> str:
        """Generate human-readable reasoning for the preference decision"""
        
        if preference == "unclear":
            return "Unable to determine clear preference from input. No strong indicators found."
        
        reasoning_parts = []
        
        # Add score information
        if preference == "visual":
            reasoning_parts.append(f"Strong visual preference detected (score: {visual_score:.1f} vs {text_score:.1f})")
        elif preference == "text":
            reasoning_parts.append(f"Strong text preference detected (score: {text_score:.1f} vs {visual_score:.1f})")
        else:
            reasoning_parts.append(f"Mixed preference detected (visual: {visual_score:.1f}, text: {text_score:.1f})")
        
        # Add keyword information
        visual_keywords = len(keyword_analysis["found_keywords"]["visual"])
        text_keywords = len(keyword_analysis["found_keywords"]["text"])
        
        if visual_keywords > 0:
            reasoning_parts.append(f"{visual_keywords} visual keyword(s) found")
        if text_keywords > 0:
            reasoning_parts.append(f"{text_keywords} text keyword(s) found")
        
        # Add phrase information
        if phrase_analysis["visual_phrases"]:
            reasoning_parts.append(f"Visual context phrases: {', '.join(phrase_analysis['visual_phrases'][:2])}")
        if phrase_analysis["text_phrases"]:
            reasoning_parts.append(f"Text context phrases: {', '.join(phrase_analysis['text_phrases'][:2])}")
        
        # Add intensity information
        if intensity_analysis["intensity_level"] != "medium":
            reasoning_parts.append(f"Intensity level: {intensity_analysis['intensity_level']}")
        
        return ". ".join(reasoning_parts) + "."
    
    def _extract_specific_requests(self, text: str) -> List[str]:
        """Extract specific requests or requirements from the text"""
        specific_requests = []
        
        # Common request patterns
        request_patterns = [
            r"show me (\w+(?:\s+\w+)*)",
            r"I want (\w+(?:\s+\w+)*)",
            r"I need (\w+(?:\s+\w+)*)",
            r"prefer (\w+(?:\s+\w+)*)",
            r"like (\w+(?:\s+\w+)*)",
            r"display (\w+(?:\s+\w+)*)",
            r"include (\w+(?:\s+\w+)*)"
        ]
        
        for pattern in request_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            specific_requests.extend(matches)
        
        # Remove duplicates and return first 5
        return list(dict.fromkeys(specific_requests))[:5]
    
    def _create_empty_response(self) -> Dict[str, Any]:
        """Create response for empty or invalid input"""
        return {
            "preference": "unclear",
            "confidence": 0.0,
            "reasoning": "No input provided or input is too short to analyze.",
            "keywords_found": {"visual": [], "text": []},
            "intensity": "low",
            "specific_requests": [],
            "fallback_preference": "mixed",
            "metadata": {
                "visual_score": 0.0,
                "text_score": 0.0,
                "total_keywords": 0,
                "has_negations": False,
                "intensity_score": 0,
                "analysis_timestamp": datetime.now().isoformat(),
                "input_length": 0,
                "processing_version": "2.0"
            }
        }
    
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """Get statistics about parsing performance"""
        if not self.parsing_history:
            return {"total_parses": 0, "average_confidence": 0.0}
        
        total_parses = len(self.parsing_history)
        avg_confidence = sum(p["result"]["confidence"] for p in self.parsing_history) / total_parses
        
        preference_distribution = {}
        for parse in self.parsing_history:
            pref = parse["result"]["preference"]
            preference_distribution[pref] = preference_distribution.get(pref, 0) + 1
        
        return {
            "total_parses": total_parses,
            "average_confidence": round(avg_confidence, 2),
            "preference_distribution": preference_distribution,
            "recent_parses": self.parsing_history[-5:] if len(self.parsing_history) >= 5 else self.parsing_history
        }


# Example usage and testing
def test_preference_parser():
    """Test the preference parser with various inputs"""
    parser = AdvancedPreferenceParser()
    
    test_cases = [
        "I prefer charts and graphs",
        "Give me detailed text explanations", 
        "I like visual data with some text explanation",
        "Show me charts but also include detailed analysis",
        "I don't like graphs, prefer written summaries",
        "Visual dashboard with brief text",
        "Comprehensive text breakdown with supporting visuals",
        "I'm a visual learner, charts help me understand better",
        "Detailed step-by-step explanations work best for me",
        "Mixed format - both charts and detailed text please"
    ]
    
    print("🧪 Testing Advanced Preference Parser")
    print("=" * 60)
    
    for i, test_input in enumerate(test_cases, 1):
        result = parser.parse_user_preference(test_input)
        print(f"\nTest {i}: '{test_input}'")
        print(f"Result: {result['preference']} (confidence: {result['confidence']})")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Keywords: {result['keywords_found']}")
        print("-" * 40)
    
    # Show statistics
    stats = parser.get_parsing_statistics()
    print(f"\n📊 Parsing Statistics:")
    print(f"Total parses: {stats['total_parses']}")
    print(f"Average confidence: {stats['average_confidence']}")
    print(f"Preference distribution: {stats['preference_distribution']}")


if __name__ == "__main__":
    test_preference_parser()