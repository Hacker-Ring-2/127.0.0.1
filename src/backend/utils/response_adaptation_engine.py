"""
Response Adaptation Engine for TheNZT AI System
Implements Step 2: Apply Preference to Existing Responses (20 points)

This module dynamically adapts AI responses based on user preferences,
reordering content, adjusting emphasis, and optimizing presentation format.
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

class ResponseType(Enum):
    TEXT_ANALYSIS = "text_analysis"
    CHART_DATA = "chart_data"
    MIXED_CONTENT = "mixed_content"
    RAW_DATA = "raw_data"
    SUMMARY = "summary"
    DETAILED_EXPLANATION = "detailed_explanation"

class PreferenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ContentBlock:
    """Represents a block of content that can be reordered/modified"""
    content_type: ResponseType
    content: str
    priority: int  # 1-10, higher is more important
    size_weight: float  # 0.1-2.0, affects display size
    metadata: Dict[str, Any]

@dataclass
class AdaptationRule:
    """Defines how to adapt content based on preferences"""
    preference_type: str  # "visual", "text", "mixed"
    content_type: ResponseType
    priority_boost: int
    size_multiplier: float
    position_preference: str  # "top", "bottom", "middle"
    visibility_threshold: float  # 0.0-1.0

class ResponseAdaptationEngine:
    """
    World-class response adaptation engine that transforms AI responses
    based on user preferences with sophisticated content reordering
    """
    
    def __init__(self):
        self.adaptation_rules = self._initialize_adaptation_rules()
        self.adaptation_history = []
        self.performance_metrics = {
            "total_adaptations": 0,
            "visual_preference_adaptations": 0,
            "text_preference_adaptations": 0,
            "mixed_preference_adaptations": 0,
            "average_adaptation_time": 0.0
        }
    
    def adapt_response(self, 
                      original_response: Dict[str, Any], 
                      user_preferences: Dict[str, Any],
                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Main adaptation function that transforms responses based on preferences
        
        Args:
            original_response: The original AI response
            user_preferences: User preference data from parser
            context: Additional context for adaptation
            
        Returns:
            Adapted response with reordered/modified content
        """
        start_time = datetime.now()
        
        try:
            # Parse and analyze the original response
            content_blocks = self._parse_response_content(original_response)
            
            # Apply preference-based adaptations
            adapted_blocks = self._apply_preference_adaptations(
                content_blocks, user_preferences, context
            )
            
            # Reorder content based on preferences
            reordered_blocks = self._reorder_content(adapted_blocks, user_preferences)
            
            # Generate adapted response structure
            adapted_response = self._construct_adapted_response(
                reordered_blocks, original_response, user_preferences
            )
            
            # Add adaptation metadata
            adapted_response["adaptation_metadata"] = self._generate_adaptation_metadata(
                original_response, user_preferences, start_time
            )
            
            # Update performance metrics
            self._update_performance_metrics(user_preferences["preference"], start_time)
            
            # Store adaptation history
            self._store_adaptation_history(original_response, adapted_response, user_preferences)
            
            return adapted_response
            
        except Exception as e:
            # Graceful fallback to original response
            return {
                **original_response,
                "adaptation_error": str(e),
                "fallback_used": True,
                "adaptation_metadata": {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def _parse_response_content(self, response: Dict[str, Any]) -> List[ContentBlock]:
        """Parse response into manageable content blocks"""
        content_blocks = []
        
        # Handle different response structures
        if "text_response" in response:
            # Parse text content
            text_blocks = self._parse_text_content(response["text_response"])
            content_blocks.extend(text_blocks)
        
        if "chart_data" in response:
            # Parse chart content
            chart_blocks = self._parse_chart_content(response["chart_data"])
            content_blocks.extend(chart_blocks)
        
        if "data" in response:
            # Parse raw data content
            data_blocks = self._parse_data_content(response["data"])
            content_blocks.extend(data_blocks)
        
        if "summary" in response:
            # Parse summary content
            summary_blocks = self._parse_summary_content(response["summary"])
            content_blocks.extend(summary_blocks)
        
        # If no specific structure found, treat as mixed content
        if not content_blocks:
            content_blocks.append(ContentBlock(
                content_type=ResponseType.MIXED_CONTENT,
                content=json.dumps(response) if isinstance(response, dict) else str(response),
                priority=5,
                size_weight=1.0,
                metadata={"original_structure": True}
            ))
        
        return content_blocks
    
    def _parse_text_content(self, text_content: str) -> List[ContentBlock]:
        """Parse text content into logical blocks"""
        blocks = []
        
        # Split by common delimiters
        sections = re.split(r'\n\n+|\n={3,}|\n-{3,}', text_content)
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
                
            # Determine content type based on content analysis
            content_type = self._analyze_text_type(section)
            
            # Determine priority based on position and content
            priority = max(1, 8 - i)  # Earlier sections get higher priority
            
            # Adjust priority based on content type
            if "summary" in section.lower() or "conclusion" in section.lower():
                priority += 2
            elif "introduction" in section.lower() or "overview" in section.lower():
                priority += 1
            
            blocks.append(ContentBlock(
                content_type=content_type,
                content=section.strip(),
                priority=min(10, priority),
                size_weight=len(section) / 1000.0,  # Weight by length
                metadata={
                    "section_index": i,
                    "word_count": len(section.split()),
                    "has_numbers": bool(re.search(r'\d+', section)),
                    "has_technical_terms": self._has_technical_terms(section)
                }
            ))
        
        return blocks
    
    def _parse_chart_content(self, chart_data: Dict[str, Any]) -> List[ContentBlock]:
        """Parse chart data into content blocks"""
        blocks = []
        
        if isinstance(chart_data, dict):
            for chart_type, data in chart_data.items():
                blocks.append(ContentBlock(
                    content_type=ResponseType.CHART_DATA,
                    content=json.dumps(data),
                    priority=7,  # Charts generally high priority for visual users
                    size_weight=1.5,  # Charts need more space
                    metadata={
                        "chart_type": chart_type,
                        "data_points": len(data.get("data", [])) if isinstance(data, dict) else 0,
                        "interactive": data.get("interactive", False) if isinstance(data, dict) else False
                    }
                ))
        
        return blocks
    
    def _parse_data_content(self, data_content: Any) -> List[ContentBlock]:
        """Parse raw data content into blocks"""
        blocks = []
        
        if isinstance(data_content, (list, dict)):
            blocks.append(ContentBlock(
                content_type=ResponseType.RAW_DATA,
                content=json.dumps(data_content, indent=2),
                priority=4,  # Raw data lower priority unless specifically requested
                size_weight=1.0,
                metadata={
                    "data_type": type(data_content).__name__,
                    "size": len(str(data_content)),
                    "structured": isinstance(data_content, (dict, list))
                }
            ))
        
        return blocks
    
    def _parse_summary_content(self, summary_content: str) -> List[ContentBlock]:
        """Parse summary content into blocks"""
        return [ContentBlock(
            content_type=ResponseType.SUMMARY,
            content=summary_content,
            priority=8,  # Summaries generally high priority
            size_weight=0.8,  # Summaries are typically concise
            metadata={
                "word_count": len(summary_content.split()),
                "has_bullet_points": "•" in summary_content or "*" in summary_content,
                "has_numbers": bool(re.search(r'\d+', summary_content))
            }
        )]
    
    def _analyze_text_type(self, text: str) -> ResponseType:
        """Analyze text to determine its type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["summary", "conclusion", "overview", "tldr"]):
            return ResponseType.SUMMARY
        elif any(word in text_lower for word in ["detailed", "comprehensive", "step-by-step", "analysis"]):
            return ResponseType.DETAILED_EXPLANATION
        elif re.search(r'\d+.*%|\$\d+|statistics|data shows', text):
            return ResponseType.TEXT_ANALYSIS
        else:
            return ResponseType.MIXED_CONTENT
    
    def _has_technical_terms(self, text: str) -> bool:
        """Check if text contains technical terms"""
        technical_indicators = [
            "algorithm", "implementation", "configuration", "optimization",
            "parameter", "variable", "function", "method", "API", "database",
            "framework", "library", "dependency", "architecture", "protocol"
        ]
        return any(term in text.lower() for term in technical_indicators)
    
    def _apply_preference_adaptations(self, 
                                    content_blocks: List[ContentBlock],
                                    user_preferences: Dict[str, Any],
                                    context: Optional[Dict[str, Any]]) -> List[ContentBlock]:
        """Apply preference-based adaptations to content blocks"""
        
        preference_type = user_preferences.get("preference", "mixed")
        confidence = user_preferences.get("confidence", 0.5)
        intensity = user_preferences.get("intensity", "medium")
        
        adapted_blocks = []
        
        for block in content_blocks:
            adapted_block = self._adapt_single_block(
                block, preference_type, confidence, intensity, context
            )
            adapted_blocks.append(adapted_block)
        
        return adapted_blocks
    
    def _adapt_single_block(self, 
                           block: ContentBlock,
                           preference_type: str,
                           confidence: float,
                           intensity: str,
                           context: Optional[Dict[str, Any]]) -> ContentBlock:
        """Adapt a single content block based on preferences"""
        
        # Find matching adaptation rule
        matching_rule = self._find_matching_rule(block.content_type, preference_type)
        
        if not matching_rule:
            return block  # No adaptation needed
        
        # Apply adaptation rule
        new_priority = block.priority + matching_rule.priority_boost
        new_size_weight = block.size_weight * matching_rule.size_multiplier
        
        # Adjust based on confidence
        confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5 to 1.0
        new_priority = int(new_priority * confidence_multiplier)
        new_size_weight = new_size_weight * confidence_multiplier
        
        # Adjust based on intensity
        intensity_multipliers = {"high": 1.3, "medium": 1.0, "low": 0.7}
        intensity_mult = intensity_multipliers.get(intensity, 1.0)
        new_priority = int(new_priority * intensity_mult)
        new_size_weight = new_size_weight * intensity_mult
        
        # Create adapted block
        adapted_block = ContentBlock(
            content_type=block.content_type,
            content=self._adapt_block_content(block.content, preference_type, matching_rule),
            priority=max(1, min(10, new_priority)),
            size_weight=max(0.1, min(3.0, new_size_weight)),
            metadata={
                **block.metadata,
                "adapted": True,
                "original_priority": block.priority,
                "original_size_weight": block.size_weight,
                "adaptation_rule": matching_rule.__dict__,
                "confidence_applied": confidence,
                "intensity_applied": intensity
            }
        )
        
        return adapted_block
    
    def _adapt_block_content(self, 
                           content: str, 
                           preference_type: str, 
                           rule: AdaptationRule) -> str:
        """Adapt the actual content based on preferences"""
        
        if preference_type == "visual" and rule.content_type == ResponseType.TEXT_ANALYSIS:
            # For visual preference, make text more scannable
            content = self._make_text_scannable(content)
        elif preference_type == "text" and rule.content_type == ResponseType.CHART_DATA:
            # For text preference, add descriptive text to charts
            content = self._add_chart_description(content)
        elif preference_type == "mixed":
            # For mixed preference, add connective elements
            content = self._add_connective_elements(content)
        
        return content
    
    def _make_text_scannable(self, text: str) -> str:
        """Make text more scannable for visual users"""
        # Add bullet points where appropriate
        sentences = text.split('. ')
        if len(sentences) > 3:
            bullet_text = "Key points:\n"
            for sentence in sentences[:3]:
                if sentence.strip():
                    bullet_text += f"• {sentence.strip()}\n"
            if len(sentences) > 3:
                remaining_text = '. '.join(sentences[3:])
                bullet_text += f"\nDetails: {remaining_text}"
            return bullet_text
        return text
    
    def _add_chart_description(self, chart_json: str) -> str:
        """Add descriptive text to chart data for text-preferring users"""
        try:
            chart_data = json.loads(chart_json)
            description = f"Chart Description: This visualization shows "
            
            # Add basic description based on chart structure
            if "data" in chart_data:
                data_points = len(chart_data["data"])
                description += f"{data_points} data points"
            
            if "title" in chart_data:
                description += f" for {chart_data['title']}"
            
            description += ".\n\n" + chart_json
            return description
        except:
            return chart_json
    
    def _add_connective_elements(self, content: str) -> str:
        """Add connective elements for mixed preference users"""
        # Add transition phrases to make content flow better
        if len(content) > 200:
            content = "Overview: " + content
        return content
    
    def _find_matching_rule(self, content_type: ResponseType, preference_type: str) -> Optional[AdaptationRule]:
        """Find the best matching adaptation rule"""
        for rule in self.adaptation_rules:
            if (rule.preference_type == preference_type and 
                rule.content_type == content_type):
                return rule
        
        # Fallback: find rule for same preference type, different content type
        for rule in self.adaptation_rules:
            if rule.preference_type == preference_type:
                return rule
        
        return None
    
    def _reorder_content(self, 
                        content_blocks: List[ContentBlock],
                        user_preferences: Dict[str, Any]) -> List[ContentBlock]:
        """Reorder content blocks based on user preferences"""
        
        preference_type = user_preferences.get("preference", "mixed")
        
        # Sort by priority (descending) and then by preference-specific criteria
        if preference_type == "visual":
            # Visual users: charts first, then summaries, then detailed text
            content_blocks.sort(key=lambda x: (
                -x.priority,
                0 if x.content_type == ResponseType.CHART_DATA else 1,
                0 if x.content_type == ResponseType.SUMMARY else 1,
                x.metadata.get("section_index", 0)
            ))
        elif preference_type == "text":
            # Text users: summaries first, then detailed explanations, then charts
            content_blocks.sort(key=lambda x: (
                -x.priority,
                0 if x.content_type == ResponseType.SUMMARY else 1,
                0 if x.content_type == ResponseType.DETAILED_EXPLANATION else 1,
                1 if x.content_type == ResponseType.CHART_DATA else 0
            ))
        else:
            # Mixed users: balanced approach
            content_blocks.sort(key=lambda x: (
                -x.priority,
                x.metadata.get("section_index", 0)
            ))
        
        return content_blocks
    
    def _construct_adapted_response(self, 
                                  content_blocks: List[ContentBlock],
                                  original_response: Dict[str, Any],
                                  user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Construct the final adapted response"""
        
        adapted_response = {
            "adapted_content": [],
            "content_order": [],
            "preference_applied": user_preferences.get("preference", "mixed"),
            "confidence_level": user_preferences.get("confidence", 0.5),
            "total_blocks": len(content_blocks)
        }
        
        # Add original response data
        for key, value in original_response.items():
            if key not in ["adaptation_metadata", "adapted_content"]:
                adapted_response[key] = value
        
        # Process content blocks in new order
        for i, block in enumerate(content_blocks):
            block_data = {
                "position": i + 1,
                "content_type": block.content_type.value,
                "content": block.content,
                "priority": block.priority,
                "size_weight": block.size_weight,
                "metadata": block.metadata
            }
            
            adapted_response["adapted_content"].append(block_data)
            adapted_response["content_order"].append(block.content_type.value)
        
        return adapted_response
    
    def _generate_adaptation_metadata(self, 
                                    original_response: Dict[str, Any],
                                    user_preferences: Dict[str, Any],
                                    start_time: datetime) -> Dict[str, Any]:
        """Generate metadata about the adaptation process"""
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "adaptation_timestamp": datetime.now().isoformat(),
            "processing_time_seconds": round(processing_time, 3),
            "user_preference": user_preferences.get("preference", "unknown"),
            "confidence_score": user_preferences.get("confidence", 0.0),
            "intensity_level": user_preferences.get("intensity", "medium"),
            "rules_applied": len(self.adaptation_rules),
            "original_structure_preserved": True,
            "adaptation_version": "2.0",
            "fallback_used": False
        }
    
    def _update_performance_metrics(self, preference_type: str, start_time: datetime):
        """Update performance tracking metrics"""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        self.performance_metrics["total_adaptations"] += 1
        
        if preference_type == "visual":
            self.performance_metrics["visual_preference_adaptations"] += 1
        elif preference_type == "text":
            self.performance_metrics["text_preference_adaptations"] += 1
        else:
            self.performance_metrics["mixed_preference_adaptations"] += 1
        
        # Update average processing time
        total_adaptations = self.performance_metrics["total_adaptations"]
        current_avg = self.performance_metrics["average_adaptation_time"]
        new_avg = ((current_avg * (total_adaptations - 1)) + processing_time) / total_adaptations
        self.performance_metrics["average_adaptation_time"] = round(new_avg, 4)
    
    def _store_adaptation_history(self, 
                                original_response: Dict[str, Any],
                                adapted_response: Dict[str, Any],
                                user_preferences: Dict[str, Any]):
        """Store adaptation history for learning and improvement"""
        
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "original_content_blocks": len(original_response.get("adapted_content", [original_response])),
            "adapted_content_blocks": len(adapted_response.get("adapted_content", [])),
            "preference_type": user_preferences.get("preference"),
            "confidence": user_preferences.get("confidence"),
            "intensity": user_preferences.get("intensity"),
            "processing_time": adapted_response.get("adaptation_metadata", {}).get("processing_time_seconds", 0)
        }
        
        self.adaptation_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self.adaptation_history) > 100:
            self.adaptation_history = self.adaptation_history[-100:]
    
    def _initialize_adaptation_rules(self) -> List[AdaptationRule]:
        """Initialize adaptation rules for different preference/content combinations"""
        
        rules = [
            # Visual preference rules
            AdaptationRule(
                preference_type="visual",
                content_type=ResponseType.CHART_DATA,
                priority_boost=3,
                size_multiplier=1.5,
                position_preference="top",
                visibility_threshold=0.8
            ),
            AdaptationRule(
                preference_type="visual",
                content_type=ResponseType.SUMMARY,
                priority_boost=2,
                size_multiplier=1.2,
                position_preference="top",
                visibility_threshold=0.9
            ),
            AdaptationRule(
                preference_type="visual",
                content_type=ResponseType.TEXT_ANALYSIS,
                priority_boost=-1,
                size_multiplier=0.8,
                position_preference="bottom",
                visibility_threshold=0.6
            ),
            
            # Text preference rules
            AdaptationRule(
                preference_type="text",
                content_type=ResponseType.DETAILED_EXPLANATION,
                priority_boost=3,
                size_multiplier=1.4,
                position_preference="top",
                visibility_threshold=0.9
            ),
            AdaptationRule(
                preference_type="text",
                content_type=ResponseType.SUMMARY,
                priority_boost=2,
                size_multiplier=1.2,
                position_preference="top",
                visibility_threshold=0.8
            ),
            AdaptationRule(
                preference_type="text",
                content_type=ResponseType.CHART_DATA,
                priority_boost=-2,
                size_multiplier=0.7,
                position_preference="bottom",
                visibility_threshold=0.4
            ),
            
            # Mixed preference rules
            AdaptationRule(
                preference_type="mixed",
                content_type=ResponseType.MIXED_CONTENT,
                priority_boost=1,
                size_multiplier=1.0,
                position_preference="middle",
                visibility_threshold=0.7
            ),
            AdaptationRule(
                preference_type="mixed",
                content_type=ResponseType.SUMMARY,
                priority_boost=2,
                size_multiplier=1.1,
                position_preference="top",
                visibility_threshold=0.8
            )
        ]
        
        return rules
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        return {
            **self.performance_metrics,
            "adaptation_history_length": len(self.adaptation_history),
            "rules_configured": len(self.adaptation_rules)
        }


# Example usage and testing
def test_response_adaptation():
    """Test the response adaptation engine"""
    
    engine = ResponseAdaptationEngine()
    
    # Sample original response
    original_response = {
        "text_response": "This is a detailed analysis of the data. The findings show significant trends in user behavior. Key insights include increased engagement and improved satisfaction scores.",
        "chart_data": {
            "line_chart": {
                "data": [{"x": 1, "y": 10}, {"x": 2, "y": 15}, {"x": 3, "y": 8}],
                "title": "User Engagement Over Time"
            }
        },
        "summary": "Overall, the data indicates positive trends in user metrics."
    }
    
    # Sample user preferences
    user_preferences = {
        "preference": "visual",
        "confidence": 0.8,
        "intensity": "high",
        "reasoning": "User prefers charts and visual data"
    }
    
    # Test adaptation
    adapted_response = engine.adapt_response(original_response, user_preferences)
    
    print("🔧 Testing Response Adaptation Engine")
    print("=" * 60)
    print(f"Original response keys: {list(original_response.keys())}")
    print(f"Adapted response keys: {list(adapted_response.keys())}")
    print(f"Content blocks created: {adapted_response.get('total_blocks', 0)}")
    print(f"Preference applied: {adapted_response.get('preference_applied')}")
    print(f"Processing time: {adapted_response.get('adaptation_metadata', {}).get('processing_time_seconds', 0)} seconds")
    
    # Show performance metrics
    metrics = engine.get_performance_metrics()
    print(f"\n📊 Performance Metrics:")
    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    test_response_adaptation()