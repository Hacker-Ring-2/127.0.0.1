"""
Enhanced Response Adapter for TheNZT AI System
Implements Step 2: Apply Preference to Existing Responses (20 points)

This module adapts AI responses based on user preferences, reordering content,
adjusting emphasis, and optimizing presentation format.
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class ResponseAdapter:
    """
    Intelligent response adapter that transforms AI responses based on user preferences
    """
    
    def __init__(self):
        self.adaptation_rules = {
            'visual': {
                'chart_priority': 'high',
                'text_length': 'brief',
                'visual_emphasis': True,
                'content_order': ['charts', 'summary', 'details']
            },
            'text': {
                'chart_priority': 'low', 
                'text_length': 'detailed',
                'visual_emphasis': False,
                'content_order': ['summary', 'details', 'charts']
            },
            'mixed': {
                'chart_priority': 'medium',
                'text_length': 'balanced',
                'visual_emphasis': False,
                'content_order': ['summary', 'charts', 'details']
            }
        }
        
    def adapt_response(self, original_response: Dict[str, Any], 
                      user_preference: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main adaptation function that transforms responses based on preferences
        
        Args:
            original_response: The original AI response from TheNZT agent
            user_preference: User preference data from parser
            
        Returns:
            Adapted response with reordered/modified content
        """
        
        preference_type = user_preference.get('preference', 'mixed')
        confidence = user_preference.get('confidence', 0.5)
        
        # Get adaptation rules for this preference
        rules = self.adaptation_rules.get(preference_type, self.adaptation_rules['mixed'])
        
        # Parse the original response
        content_blocks = self._parse_response_content(original_response)
        
        # Apply preference-based adaptations
        adapted_blocks = self._apply_preference_adaptations(content_blocks, rules, confidence)
        
        # Reorder content based on preference
        reordered_blocks = self._reorder_content(adapted_blocks, rules['content_order'])
        
        # Generate final response
        adapted_response = self._build_adapted_response(
            reordered_blocks, original_response, user_preference, rules
        )
        
        return adapted_response
    
    def _parse_response_content(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse response into manageable content blocks"""
        blocks = []
        
        # Parse different types of content
        if 'final_response' in response:
            text_content = response['final_response']
            
            # Look for chart/graph generation calls in the text
            chart_matches = re.findall(r'graph_generation_tool.*?```', text_content, re.DOTALL)
            
            if chart_matches:
                blocks.append({
                    'type': 'charts',
                    'content': chart_matches,
                    'priority': 3,
                    'metadata': {'chart_count': len(chart_matches)}
                })
            
            # Extract text summaries (usually at beginning)
            lines = text_content.split('\n')
            summary_lines = []
            detail_lines = []
            
            in_summary = True
            for line in lines:
                if any(keyword in line.lower() for keyword in ['analysis', 'detailed', 'breakdown', 'furthermore']):
                    in_summary = False
                
                if in_summary and line.strip():
                    summary_lines.append(line)
                elif line.strip():
                    detail_lines.append(line)
            
            if summary_lines:
                blocks.append({
                    'type': 'summary',
                    'content': '\n'.join(summary_lines[:5]),  # First 5 lines as summary
                    'priority': 2,
                    'metadata': {'line_count': len(summary_lines)}
                })
            
            if detail_lines:
                blocks.append({
                    'type': 'details',
                    'content': '\n'.join(detail_lines),
                    'priority': 1,
                    'metadata': {'line_count': len(detail_lines)}
                })
        
        # Handle messages array (from LangGraph agent)
        if 'messages' in response:
            for message in response['messages']:
                if isinstance(message, dict) and 'content' in message:
                    content = message['content']
                    if 'graph_generation_tool' in content:
                        blocks.append({
                            'type': 'charts',
                            'content': content,
                            'priority': 3,
                            'metadata': {'from_messages': True}
                        })
        
        return blocks if blocks else [{'type': 'text', 'content': str(response), 'priority': 1, 'metadata': {}}]
    
    def _apply_preference_adaptations(self, blocks: List[Dict[str, Any]], 
                                    rules: Dict[str, Any], confidence: float) -> List[Dict[str, Any]]:
        """Apply preference-based adaptations to content blocks"""
        
        adapted_blocks = []
        
        for block in blocks:
            adapted_block = block.copy()
            
            # Adjust priority based on preference
            if block['type'] == 'charts' and rules['chart_priority'] == 'high':
                adapted_block['priority'] += int(2 * confidence)
            elif block['type'] == 'charts' and rules['chart_priority'] == 'low':
                adapted_block['priority'] -= int(1 * confidence)
            
            # Adjust text length
            if block['type'] in ['summary', 'details']:
                if rules['text_length'] == 'brief':
                    adapted_block['content'] = self._shorten_text(block['content'])
                elif rules['text_length'] == 'detailed':
                    adapted_block['content'] = self._expand_text(block['content'])
            
            # Add visual emphasis metadata
            adapted_block['visual_emphasis'] = rules['visual_emphasis']
            adapted_block['confidence_applied'] = confidence
            
            adapted_blocks.append(adapted_block)
        
        return adapted_blocks
    
    def _reorder_content(self, blocks: List[Dict[str, Any]], order: List[str]) -> List[Dict[str, Any]]:
        """Reorder content blocks based on preference"""
        
        reordered = []
        
        # First, add blocks in preferred order
        for content_type in order:
            for block in blocks:
                if block['type'] == content_type:
                    reordered.append(block)
        
        # Then add any remaining blocks
        for block in blocks:
            if block not in reordered:
                reordered.append(block)
        
        return reordered
    
    def _build_adapted_response(self, blocks: List[Dict[str, Any]], 
                              original_response: Dict[str, Any],
                              user_preference: Dict[str, Any],
                              rules: Dict[str, Any]) -> Dict[str, Any]:
        """Build the final adapted response"""
        
        # Combine content based on new order
        adapted_content = []
        visual_content = []
        text_content = []
        
        for block in blocks:
            if block['type'] == 'charts':
                visual_content.append(block['content'])
            else:
                text_content.append(block['content'])
        
        # Create preference-aware response structure
        response_structure = {
            'adapted_response': {
                'visual_content': visual_content,
                'text_content': text_content,
                'content_blocks': blocks,
                'preference_applied': user_preference.get('preference', 'mixed'),
                'confidence_level': user_preference.get('confidence', 0.5),
                'adaptation_timestamp': datetime.now().isoformat()
            },
            'original_response': original_response,
            'adaptation_metadata': {
                'rules_applied': rules,
                'blocks_reordered': len(blocks),
                'visual_emphasis': rules['visual_emphasis'],
                'content_order': rules['content_order']
            }
        }
        
        return response_structure
    
    def _shorten_text(self, text: str) -> str:
        """Shorten text for visual-preference users"""
        sentences = text.split('.')
        if len(sentences) <= 2:
            return text
        
        # Keep first 2 sentences and add summary
        shortened = '. '.join(sentences[:2]) + '.'
        if len(sentences) > 2:
            shortened += f" (Additional details available - {len(sentences)-2} more points)"
        
        return shortened
    
    def _expand_text(self, text: str) -> str:
        """Expand text for text-preference users"""
        # Add more descriptive language for text-preferring users
        if len(text) < 100:
            return f"Comprehensive Analysis: {text}\n\nThis analysis provides detailed insights into the key aspects of your query."
        return text
    
    def format_for_display(self, adapted_response: Dict[str, Any]) -> str:
        """Format adapted response for display"""
        
        adapted = adapted_response['adapted_response']
        preference = adapted['preference_applied']
        
        display_content = f"## Personalized Response (Optimized for {preference.upper()} preference)\n\n"
        
        # Add content based on blocks order
        for block in adapted['content_blocks']:
            if block['type'] == 'summary':
                display_content += f"### Summary\n{block['content']}\n\n"
            elif block['type'] == 'details':
                display_content += f"### Detailed Analysis\n{block['content']}\n\n"
            elif block['type'] == 'charts':
                if preference == 'visual':
                    display_content += f"### 📊 Visual Data (Primary Focus)\n"
                else:
                    display_content += f"### 📊 Supporting Visuals\n"
                display_content += f"[Chart content would be rendered here]\n\n"
        
        # Add preference note
        confidence = adapted['confidence_level']
        if confidence > 0.7:
            confidence_text = "high confidence"
        elif confidence > 0.4:
            confidence_text = "medium confidence"
        else:
            confidence_text = "low confidence"
            
        display_content += f"\n---\n*Response adapted for {preference} preference with {confidence_text}*"
        
        return display_content


# Test function
def test_response_adapter():
    """Test the response adapter"""
    adapter = ResponseAdapter()
    
    # Sample original response (mimicking TheNZT agent output)
    sample_response = {
        'final_response': '''Tesla Stock Analysis Summary:
        
Tesla (TSLA) is currently showing strong performance indicators. The company's revenue growth has been consistent over the past quarters.

Detailed Financial Analysis:
Tesla's revenue for Q3 2024 reached $25.2 billion, representing a 15% increase year-over-year. The automotive segment continues to drive growth.

Furthermore, the energy storage business has shown remarkable expansion with 2.1 GWh deployed in the quarter.

graph_generation_tool(table_data="Tesla Revenue: Q1: $21.3B, Q2: $24.9B, Q3: $25.2B")

Additional market analysis shows Tesla maintaining its position as the leading EV manufacturer.''',
        'messages': []
    }
    
    # Test different preferences
    preferences = [
        {'preference': 'visual', 'confidence': 0.8, 'reasoning': 'User prefers charts'},
        {'preference': 'text', 'confidence': 0.9, 'reasoning': 'User prefers detailed text'},
        {'preference': 'mixed', 'confidence': 0.6, 'reasoning': 'User wants balanced content'}
    ]
    
    print("🔧 Testing Response Adapter")
    print("=" * 60)
    
    for i, pref in enumerate(preferences, 1):
        print(f"\n--- Test {i}: {pref['preference'].upper()} Preference ---")
        adapted = adapter.adapt_response(sample_response, pref)
        
        print(f"Content blocks: {len(adapted['adapted_response']['content_blocks'])}")
        print(f"Visual content blocks: {len(adapted['adapted_response']['visual_content'])}")
        print(f"Text content blocks: {len(adapted['adapted_response']['text_content'])}")
        print(f"Content order: {adapted['adaptation_metadata']['content_order']}")
        
        # Show formatted output
        formatted = adapter.format_for_display(adapted)
        print(f"Formatted length: {len(formatted)} characters")


if __name__ == "__main__":
    test_response_adapter()