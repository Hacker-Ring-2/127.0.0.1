"""
Backend Integration for Preference-Aware Balance System
Integrates with TheNZT AI agents for preference detection
"""

from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
import re
from enum import Enum

class PreferenceType(Enum):
    VISUAL = "visual"
    TEXT = "text"
    MIXED = "mixed"
    UNCLEAR = "unclear"

class ConfidenceLevel(Enum):
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95

@dataclass
class PreferenceData:
    preference: PreferenceType
    confidence: float
    reasoning: str
    keywords_found: List[str]
    user_context: Optional[Dict] = None

class PreferenceDetectionAgent:
    """
    Agent that analyzes user queries to detect presentation preferences
    Integrates with TheNZT AI system for Step 3: Customize Chart/Text Balance
    """
    
    def __init__(self):
        # Visual preference indicators
        self.visual_keywords = {
            'strong': ['chart', 'graph', 'visualize', 'plot', 'diagram', 'show me'],
            'medium': ['visual', 'see', 'display', 'picture', 'image'],
            'weak': ['look', 'view', 'appearance']
        }
        
        # Text preference indicators
        self.text_keywords = {
            'strong': ['explain', 'describe', 'detail', 'analysis', 'summary', 'tell me'],
            'medium': ['information', 'data', 'facts', 'report', 'breakdown'],
            'weak': ['understand', 'know', 'learn']
        }
        
        # Mixed preference indicators
        self.mixed_keywords = {
            'strong': ['comprehensive', 'complete', 'both', 'everything'],
            'medium': ['overview', 'full picture', 'detailed view'],
            'weak': ['general', 'overall']
        }

    def analyze_query(self, user_query: str, user_history: Optional[List[str]] = None) -> PreferenceData:
        """
        Analyze user query to detect presentation preference
        
        Args:
            user_query: The user's input query
            user_history: Optional list of previous user queries for context
            
        Returns:
            PreferenceData object with detected preference and confidence
        """
        query_lower = user_query.lower()
        found_keywords = []
        
        # Score each preference type
        visual_score = self._calculate_preference_score(query_lower, self.visual_keywords, found_keywords, 'visual')
        text_score = self._calculate_preference_score(query_lower, self.text_keywords, found_keywords, 'text')
        mixed_score = self._calculate_preference_score(query_lower, self.mixed_keywords, found_keywords, 'mixed')
        
        # Include user history context if available
        if user_history:
            history_context = self._analyze_user_history(user_history)
            visual_score *= history_context.get('visual_multiplier', 1.0)
            text_score *= history_context.get('text_multiplier', 1.0)
            mixed_score *= history_context.get('mixed_multiplier', 1.0)
        
        # Determine preference and confidence
        max_score = max(visual_score, text_score, mixed_score)
        
        if max_score < 0.3:
            preference = PreferenceType.UNCLEAR
            confidence = 0.2
            reasoning = "No clear preference indicators found in query"
        elif visual_score == max_score:
            preference = PreferenceType.VISUAL
            confidence = min(0.95, visual_score)
            reasoning = f"Strong visual indicators detected: {', '.join([k for k in found_keywords if k in self._flatten_keywords(self.visual_keywords)])}"
        elif text_score == max_score:
            preference = PreferenceType.TEXT
            confidence = min(0.95, text_score)
            reasoning = f"Strong text/analysis indicators detected: {', '.join([k for k in found_keywords if k in self._flatten_keywords(self.text_keywords)])}"
        else:
            preference = PreferenceType.MIXED
            confidence = min(0.95, mixed_score)
            reasoning = f"Mixed preference indicators detected: {', '.join([k for k in found_keywords if k in self._flatten_keywords(self.mixed_keywords)])}"
        
        return PreferenceData(
            preference=preference,
            confidence=confidence,
            reasoning=reasoning,
            keywords_found=found_keywords,
            user_context={"query_length": len(user_query), "history_count": len(user_history) if user_history else 0}
        )

    def _calculate_preference_score(self, query: str, keywords_dict: Dict, found_keywords: List[str], pref_type: str) -> float:
        """Calculate preference score based on keyword matches"""
        score = 0.0
        
        for strength, keywords in keywords_dict.items():
            for keyword in keywords:
                if keyword in query:
                    found_keywords.append(keyword)
                    if strength == 'strong':
                        score += 0.4
                    elif strength == 'medium':
                        score += 0.25
                    else:  # weak
                        score += 0.1
        
        # Bonus for multiple matches
        matches = len([k for k in found_keywords if k in self._flatten_keywords(keywords_dict)])
        if matches > 1:
            score *= (1 + (matches - 1) * 0.1)
        
        return min(1.0, score)

    def _analyze_user_history(self, history: List[str]) -> Dict[str, float]:
        """Analyze user history to adjust preference detection"""
        visual_count = 0
        text_count = 0
        mixed_count = 0
        
        for query in history[-5:]:  # Only look at last 5 queries
            query_lower = query.lower()
            
            if any(keyword in query_lower for keyword in self._flatten_keywords(self.visual_keywords)):
                visual_count += 1
            if any(keyword in query_lower for keyword in self._flatten_keywords(self.text_keywords)):
                text_count += 1
            if any(keyword in query_lower for keyword in self._flatten_keywords(self.mixed_keywords)):
                mixed_count += 1
        
        total = len(history[-5:])
        return {
            'visual_multiplier': 1.0 + (visual_count / total) * 0.3,
            'text_multiplier': 1.0 + (text_count / total) * 0.3,
            'mixed_multiplier': 1.0 + (mixed_count / total) * 0.3
        }

    def _flatten_keywords(self, keywords_dict: Dict) -> List[str]:
        """Flatten nested keyword dictionary to simple list"""
        result = []
        for keywords in keywords_dict.values():
            result.extend(keywords)
        return result

# Integration with TheNZT Response Generator
class PreferenceAwareResponseGenerator:
    """
    Generates responses with appropriate chart/text balance based on detected preferences
    """
    
    def __init__(self, preference_agent: PreferenceDetectionAgent):
        self.preference_agent = preference_agent

    def generate_response(self, user_query: str, data: Dict, user_history: Optional[List[str]] = None) -> Dict:
        """
        Generate a preference-aware response
        
        Args:
            user_query: User's input query
            data: Data to be presented (charts, analysis, etc.)
            user_history: Previous user queries for context
            
        Returns:
            Dictionary containing response configuration
        """
        # Detect user preference
        preference_data = self.preference_agent.analyze_query(user_query, user_history)
        
        # Configure response based on preference
        response_config = self._create_response_config(preference_data, data)
        
        return {
            'preference_data': {
                'preference': preference_data.preference.value,
                'confidence': preference_data.confidence,
                'reasoning': preference_data.reasoning,
                'keywords_found': preference_data.keywords_found
            },
            'response_config': response_config,
            'content': self._generate_content(data, response_config)
        }

    def _create_response_config(self, preference_data: PreferenceData, data: Dict) -> Dict:
        """Create response configuration based on preference"""
        if preference_data.preference == PreferenceType.VISUAL:
            return {
                'chart_size': 'large' if preference_data.confidence > 0.7 else 'medium',
                'text_size': 'brief',
                'layout': 'visual-first',
                'emphasis': 'charts'
            }
        elif preference_data.preference == PreferenceType.TEXT:
            return {
                'chart_size': 'small',
                'text_size': 'detailed' if preference_data.confidence > 0.7 else 'balanced',
                'layout': 'text-first',
                'emphasis': 'text'
            }
        else:  # MIXED or UNCLEAR
            return {
                'chart_size': 'medium',
                'text_size': 'balanced',
                'layout': 'balanced',
                'emphasis': 'equal'
            }

    def _generate_content(self, data: Dict, config: Dict) -> Dict:
        """Generate actual content based on configuration"""
        # This would integrate with TheNZT's chart generation and text analysis
        return {
            'chart_data': data.get('chart_data', {}),
            'analysis_text': data.get('analysis', ''),
            'summary': data.get('summary', ''),
            'config': config
        }

# Example usage with TheNZT integration
def example_integration():
    """Example of how this integrates with TheNZT system"""
    
    # Initialize the preference detection system
    preference_agent = PreferenceDetectionAgent()
    response_generator = PreferenceAwareResponseGenerator(preference_agent)
    
    # Example user queries
    test_queries = [
        "Show me a chart of the stock performance",
        "Can you explain the financial analysis in detail?",
        "I want both charts and detailed explanations",
        "What's the current market situation?"
    ]
    
    # Mock data (would come from TheNZT data processing)
    mock_data = {
        'chart_data': {'dates': ['2024-01', '2024-02'], 'values': [100, 120]},
        'analysis': 'Detailed financial analysis showing 20% growth...',
        'summary': 'Portfolio shows strong performance'
    }
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = response_generator.generate_response(query, mock_data)
        print(f"Detected Preference: {response['preference_data']['preference']}")
        print(f"Confidence: {response['preference_data']['confidence']:.2f}")
        print(f"Config: {response['response_config']}")
        print("-" * 50)

if __name__ == "__main__":
    example_integration()