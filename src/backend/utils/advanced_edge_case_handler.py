"""
Advanced Edge Case Handler for TheNZT AI System
Implements Step 4: Handle Edge Cases (20 points)

This module provides comprehensive edge case handling for preference-based responses,
ensuring graceful degradation and fallback mechanisms in all scenarios.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EdgeCaseType(Enum):
    EMPTY_INPUT = "empty_input"
    MALFORMED_DATA = "malformed_data"
    CONFLICTING_PREFERENCES = "conflicting_preferences"
    MISSING_CONTENT = "missing_content"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    INVALID_CONFIGURATION = "invalid_configuration"
    NETWORK_FAILURE = "network_failure"
    PARSING_ERROR = "parsing_error"
    RENDERING_FAILURE = "rendering_failure"
    UNKNOWN_FORMAT = "unknown_format"

class FallbackStrategy(Enum):
    DEFAULT_MIXED = "default_mixed"
    CONTENT_ANALYSIS = "content_analysis"
    HISTORICAL_PREFERENCE = "historical_preference"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    ERROR_DISPLAY = "error_display"
    MINIMAL_RESPONSE = "minimal_response"

@dataclass
class EdgeCaseRule:
    """Defines how to handle specific edge cases"""
    case_type: EdgeCaseType
    detection_conditions: List[Callable[[Any], bool]]
    fallback_strategy: FallbackStrategy
    priority: int  # Higher priority rules are applied first
    recovery_actions: List[str]
    user_message: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EdgeCaseResult:
    """Result of edge case handling"""
    case_detected: EdgeCaseType
    handled: bool
    fallback_applied: str
    recovery_successful: bool
    user_message: str
    fallback_data: Dict[str, Any]
    metadata: Dict[str, Any]
    processing_time: float

class AdvancedEdgeCaseHandler:
    """
    World-class edge case handler with sophisticated detection and recovery
    """
    
    def __init__(self):
        self.edge_case_rules = self._initialize_edge_case_rules()
        self.fallback_cache = {}
        self.performance_history = []
        self.recovery_statistics = {
            "total_edge_cases": 0,
            "successful_recoveries": 0,
            "fallback_usage": {},
            "performance_degradations": 0
        }
        
    def handle_edge_cases(self, 
                         input_data: Any,
                         preferences: Optional[Dict[str, Any]] = None,
                         context: Optional[Dict[str, Any]] = None) -> EdgeCaseResult:
        """
        Main edge case handling function
        
        Args:
            input_data: The data to analyze for edge cases
            preferences: User preferences that might have issues
            context: Additional context for edge case detection
            
        Returns:
            EdgeCaseResult with handling details and fallback data
        """
        start_time = datetime.now()
        
        try:
            # Detect edge cases
            detected_cases = self._detect_edge_cases(input_data, preferences, context)
            
            if not detected_cases:
                return EdgeCaseResult(
                    case_detected=EdgeCaseType.UNKNOWN_FORMAT,  # No edge case
                    handled=False,
                    fallback_applied="none",
                    recovery_successful=True,
                    user_message="No edge cases detected",
                    fallback_data={},
                    metadata={"detection_time": (datetime.now() - start_time).total_seconds()},
                    processing_time=(datetime.now() - start_time).total_seconds()
                )
            
            # Handle the highest priority edge case
            primary_case = max(detected_cases, key=lambda x: x['priority'])
            handling_result = self._handle_single_edge_case(
                primary_case, input_data, preferences, context
            )
            
            # Update statistics
            self._update_statistics(primary_case, handling_result)
            
            return EdgeCaseResult(
                case_detected=primary_case['type'],
                handled=handling_result['handled'],
                fallback_applied=handling_result['fallback_strategy'],
                recovery_successful=handling_result['recovery_successful'],
                user_message=handling_result['user_message'],
                fallback_data=handling_result['fallback_data'],
                metadata={
                    **handling_result['metadata'],
                    "detected_cases_count": len(detected_cases),
                    "all_detected_cases": [case['type'].value for case in detected_cases]
                },
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            logger.error(f"Critical error in edge case handler: {str(e)}")
            logger.error(traceback.format_exc())
            
            return self._create_critical_error_response(e, start_time)
    
    def _detect_edge_cases(self, 
                          input_data: Any,
                          preferences: Optional[Dict[str, Any]],
                          context: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect all applicable edge cases"""
        detected_cases = []
        
        for rule in self.edge_case_rules:
            try:
                # Check if any detection condition matches
                for condition in rule.detection_conditions:
                    if condition({"input": input_data, "preferences": preferences, "context": context}):
                        detected_cases.append({
                            "type": rule.case_type,
                            "rule": rule,
                            "priority": rule.priority
                        })
                        break  # Only need one condition to match per rule
                        
            except Exception as e:
                logger.warning(f"Error in edge case detection for {rule.case_type}: {str(e)}")
                continue
        
        return detected_cases
    
    def _handle_single_edge_case(self, 
                                case_info: Dict[str, Any],
                                input_data: Any,
                                preferences: Optional[Dict[str, Any]],
                                context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle a single detected edge case"""
        
        rule = case_info['rule']
        case_type = case_info['type']
        
        try:
            # Apply the appropriate fallback strategy
            fallback_result = self._apply_fallback_strategy(
                rule.fallback_strategy, input_data, preferences, context, rule
            )
            
            # Attempt recovery actions
            recovery_successful = self._execute_recovery_actions(
                rule.recovery_actions, fallback_result, context
            )
            
            return {
                "handled": True,
                "fallback_strategy": rule.fallback_strategy.value,
                "recovery_successful": recovery_successful,
                "user_message": rule.user_message,
                "fallback_data": fallback_result,
                "metadata": {
                    "case_type": case_type.value,
                    "recovery_actions_executed": rule.recovery_actions,
                    "rule_metadata": rule.metadata
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to handle edge case {case_type}: {str(e)}")
            
            # Ultimate fallback - minimal response
            return {
                "handled": False,
                "fallback_strategy": "emergency_fallback",
                "recovery_successful": False,
                "user_message": "An unexpected error occurred. Displaying minimal response.",
                "fallback_data": self._create_minimal_fallback(),
                "metadata": {
                    "error": str(e),
                    "emergency_fallback": True
                }
            }
    
    def _apply_fallback_strategy(self, 
                               strategy: FallbackStrategy,
                               input_data: Any,
                               preferences: Optional[Dict[str, Any]],
                               context: Optional[Dict[str, Any]],
                               rule: EdgeCaseRule) -> Dict[str, Any]:
        """Apply the specified fallback strategy"""
        
        strategy_handlers = {
            FallbackStrategy.DEFAULT_MIXED: self._fallback_default_mixed,
            FallbackStrategy.CONTENT_ANALYSIS: self._fallback_content_analysis,
            FallbackStrategy.HISTORICAL_PREFERENCE: self._fallback_historical_preference,
            FallbackStrategy.GRACEFUL_DEGRADATION: self._fallback_graceful_degradation,
            FallbackStrategy.ERROR_DISPLAY: self._fallback_error_display,
            FallbackStrategy.MINIMAL_RESPONSE: self._fallback_minimal_response
        }
        
        handler = strategy_handlers.get(strategy, self._fallback_minimal_response)
        
        try:
            return handler(input_data, preferences, context, rule)
        except Exception as e:
            logger.warning(f"Fallback strategy {strategy} failed: {str(e)}")
            return self._fallback_minimal_response(input_data, preferences, context, rule)
    
    def _fallback_default_mixed(self, 
                              input_data: Any,
                              preferences: Optional[Dict[str, Any]],
                              context: Optional[Dict[str, Any]],
                              rule: EdgeCaseRule) -> Dict[str, Any]:
        """Fallback to balanced mixed preference"""
        return {
            "preference": "mixed",
            "confidence": 0.5,
            "intensity": "medium",
            "reasoning": "Applied default mixed preference due to edge case detection",
            "keywords_found": {"visual": [], "text": []},
            "specific_requests": [],
            "fallback_preference": "mixed",
            "metadata": {
                "fallback_strategy": "default_mixed",
                "original_issue": rule.case_type.value,
                "confidence_artificial": True
            }
        }
    
    def _fallback_content_analysis(self, 
                                 input_data: Any,
                                 preferences: Optional[Dict[str, Any]],
                                 context: Optional[Dict[str, Any]],
                                 rule: EdgeCaseRule) -> Dict[str, Any]:
        """Analyze available content to determine best fallback"""
        
        # Analyze input content type
        content_analysis = self._analyze_content_structure(input_data)
        
        # Determine preference based on content
        if content_analysis["has_charts"] and not content_analysis["has_text"]:
            preference = "visual"
            confidence = 0.7
        elif content_analysis["has_text"] and not content_analysis["has_charts"]:
            preference = "text"
            confidence = 0.7
        else:
            preference = "mixed"
            confidence = 0.6
        
        return {
            "preference": preference,
            "confidence": confidence,
            "intensity": "medium",
            "reasoning": f"Content analysis fallback: {content_analysis['analysis_summary']}",
            "keywords_found": {"visual": [], "text": []},
            "specific_requests": [],
            "fallback_preference": preference,
            "metadata": {
                "fallback_strategy": "content_analysis",
                "content_analysis": content_analysis,
                "original_issue": rule.case_type.value
            }
        }
    
    def _fallback_historical_preference(self, 
                                      input_data: Any,
                                      preferences: Optional[Dict[str, Any]],
                                      context: Optional[Dict[str, Any]],
                                      rule: EdgeCaseRule) -> Dict[str, Any]:
        """Use historical preference data if available"""
        
        # Try to get historical preference from context or cache
        historical_pref = None
        
        if context and "user_history" in context:
            historical_pref = self._extract_historical_preference(context["user_history"])
        
        if not historical_pref and hasattr(self, '_preference_cache'):
            historical_pref = getattr(self, '_preference_cache', {}).get("last_preference")
        
        if historical_pref:
            return {
                **historical_pref,
                "reasoning": f"Using historical preference due to {rule.case_type.value}",
                "metadata": {
                    "fallback_strategy": "historical_preference",
                    "historical_data_used": True,
                    "original_issue": rule.case_type.value
                }
            }
        else:
            # No historical data available, use default mixed
            return self._fallback_default_mixed(input_data, preferences, context, rule)
    
    def _fallback_graceful_degradation(self, 
                                     input_data: Any,
                                     preferences: Optional[Dict[str, Any]],
                                     context: Optional[Dict[str, Any]],
                                     rule: EdgeCaseRule) -> Dict[str, Any]:
        """Gracefully degrade functionality while maintaining core features"""
        
        # Attempt to salvage what we can from the original preferences
        salvaged_data = self._salvage_preference_data(preferences)
        
        return {
            "preference": salvaged_data.get("preference", "mixed"),
            "confidence": max(0.3, salvaged_data.get("confidence", 0.5) * 0.7),  # Reduce confidence
            "intensity": "low",  # Lower intensity for safety
            "reasoning": f"Graceful degradation applied due to {rule.case_type.value}",
            "keywords_found": salvaged_data.get("keywords_found", {"visual": [], "text": []}),
            "specific_requests": salvaged_data.get("specific_requests", [])[:3],  # Limit requests
            "fallback_preference": "mixed",
            "metadata": {
                "fallback_strategy": "graceful_degradation",
                "original_data_salvaged": salvaged_data,
                "degradation_applied": True,
                "original_issue": rule.case_type.value
            }
        }
    
    def _fallback_error_display(self, 
                              input_data: Any,
                              preferences: Optional[Dict[str, Any]],
                              context: Optional[Dict[str, Any]],
                              rule: EdgeCaseRule) -> Dict[str, Any]:
        """Display user-friendly error message with fallback"""
        
        error_messages = {
            EdgeCaseType.EMPTY_INPUT: "No personalization preferences provided. Using balanced display.",
            EdgeCaseType.MALFORMED_DATA: "Invalid preference format detected. Using default settings.",
            EdgeCaseType.CONFLICTING_PREFERENCES: "Conflicting preferences detected. Using balanced approach.",
            EdgeCaseType.MISSING_CONTENT: "Some content is missing. Displaying available information.",
            EdgeCaseType.PARSING_ERROR: "Unable to understand preferences. Using default mixed layout."
        }
        
        user_friendly_message = error_messages.get(
            rule.case_type, 
            "An issue was detected with your preferences. Using default settings."
        )
        
        return {
            "preference": "mixed",
            "confidence": 0.4,
            "intensity": "medium",
            "reasoning": user_friendly_message,
            "keywords_found": {"visual": [], "text": []},
            "specific_requests": [],
            "fallback_preference": "mixed",
            "metadata": {
                "fallback_strategy": "error_display",
                "user_friendly_error": user_friendly_message,
                "original_issue": rule.case_type.value,
                "show_error_message": True
            }
        }
    
    def _fallback_minimal_response(self, 
                                 input_data: Any,
                                 preferences: Optional[Dict[str, Any]],
                                 context: Optional[Dict[str, Any]],
                                 rule: EdgeCaseRule) -> Dict[str, Any]:
        """Provide minimal but functional response"""
        return {
            "preference": "mixed",
            "confidence": 0.3,
            "intensity": "low",
            "reasoning": "Minimal fallback response applied",
            "keywords_found": {"visual": [], "text": []},
            "specific_requests": [],
            "fallback_preference": "mixed",
            "metadata": {
                "fallback_strategy": "minimal_response",
                "minimal_mode": True,
                "original_issue": rule.case_type.value if rule else "unknown"
            }
        }
    
    def _analyze_content_structure(self, input_data: Any) -> Dict[str, Any]:
        """Analyze the structure of input data"""
        
        analysis = {
            "has_charts": False,
            "has_text": False,
            "has_data": False,
            "content_types": [],
            "estimated_complexity": "low",
            "analysis_summary": ""
        }
        
        try:
            if isinstance(input_data, dict):
                if any(key in str(input_data).lower() for key in ["chart", "graph", "plot", "visualization"]):
                    analysis["has_charts"] = True
                    analysis["content_types"].append("charts")
                
                if any(key in input_data for key in ["text", "content", "message", "description"]):
                    analysis["has_text"] = True
                    analysis["content_types"].append("text")
                
                if any(key in input_data for key in ["data", "values", "results"]):
                    analysis["has_data"] = True
                    analysis["content_types"].append("data")
            
            elif isinstance(input_data, str):
                if len(input_data) > 50:
                    analysis["has_text"] = True
                    analysis["content_types"].append("text")
            
            # Generate summary
            if analysis["content_types"]:
                analysis["analysis_summary"] = f"Content contains: {', '.join(analysis['content_types'])}"
            else:
                analysis["analysis_summary"] = "Content structure unclear"
            
            # Estimate complexity
            complexity_score = len(analysis["content_types"])
            if complexity_score >= 3:
                analysis["estimated_complexity"] = "high"
            elif complexity_score == 2:
                analysis["estimated_complexity"] = "medium"
            
        except Exception as e:
            logger.warning(f"Content analysis failed: {str(e)}")
            analysis["analysis_summary"] = "Content analysis failed"
        
        return analysis
    
    def _salvage_preference_data(self, preferences: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Attempt to salvage usable data from corrupted preferences"""
        
        salvaged = {}
        
        if not preferences:
            return salvaged
        
        try:
            # Try to extract basic preference
            if "preference" in preferences:
                pref_val = preferences["preference"]
                if pref_val in ["visual", "text", "mixed", "unclear"]:
                    salvaged["preference"] = pref_val
            
            # Try to extract confidence
            if "confidence" in preferences:
                conf_val = preferences["confidence"]
                if isinstance(conf_val, (int, float)) and 0 <= conf_val <= 1:
                    salvaged["confidence"] = conf_val
            
            # Try to extract keywords
            if "keywords_found" in preferences:
                keywords = preferences["keywords_found"]
                if isinstance(keywords, dict):
                    salvaged["keywords_found"] = keywords
            
            # Try to extract specific requests
            if "specific_requests" in preferences:
                requests = preferences["specific_requests"]
                if isinstance(requests, list):
                    salvaged["specific_requests"] = requests
                    
        except Exception as e:
            logger.warning(f"Data salvage failed: {str(e)}")
        
        return salvaged
    
    def _extract_historical_preference(self, user_history: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract preference from user history"""
        
        try:
            if "recent_preferences" in user_history:
                recent = user_history["recent_preferences"]
                if isinstance(recent, list) and recent:
                    return recent[0]  # Most recent preference
            
            if "preferred_format" in user_history:
                format_pref = user_history["preferred_format"]
                return {
                    "preference": format_pref,
                    "confidence": 0.6,
                    "intensity": "medium",
                    "reasoning": "Extracted from user history"
                }
                
        except Exception as e:
            logger.warning(f"Historical preference extraction failed: {str(e)}")
        
        return None
    
    def _execute_recovery_actions(self, 
                                actions: List[str],
                                fallback_result: Dict[str, Any],
                                context: Optional[Dict[str, Any]]) -> bool:
        """Execute recovery actions"""
        
        recovery_successful = True
        
        for action in actions:
            try:
                if action == "cache_fallback":
                    self._cache_fallback_result(fallback_result)
                elif action == "log_incident":
                    self._log_edge_case_incident(fallback_result, context)
                elif action == "notify_monitoring":
                    self._notify_monitoring_system(fallback_result)
                elif action == "cleanup_data":
                    self._cleanup_corrupted_data(context)
                else:
                    logger.warning(f"Unknown recovery action: {action}")
                    
            except Exception as e:
                logger.error(f"Recovery action '{action}' failed: {str(e)}")
                recovery_successful = False
        
        return recovery_successful
    
    def _cache_fallback_result(self, fallback_result: Dict[str, Any]):
        """Cache the fallback result for future use"""
        cache_key = f"fallback_{datetime.now().strftime('%Y%m%d_%H')}"
        self.fallback_cache[cache_key] = {
            "result": fallback_result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Keep only last 24 hours of cache
        cutoff_time = datetime.now().timestamp() - (24 * 3600)
        self.fallback_cache = {
            k: v for k, v in self.fallback_cache.items()
            if datetime.fromisoformat(v["timestamp"]).timestamp() > cutoff_time
        }
    
    def _log_edge_case_incident(self, fallback_result: Dict[str, Any], context: Optional[Dict[str, Any]]):
        """Log the edge case incident for analysis"""
        logger.info(f"Edge case handled: {json.dumps({
            'fallback_strategy': fallback_result.get('metadata', {}).get('fallback_strategy'),
            'case_type': fallback_result.get('metadata', {}).get('original_issue'),
            'timestamp': datetime.now().isoformat(),
            'context_available': context is not None
        })}")
    
    def _notify_monitoring_system(self, fallback_result: Dict[str, Any]):
        """Notify external monitoring system (placeholder)"""
        # In a real system, this would send alerts to monitoring tools
        logger.info(f"Monitoring notification: Edge case handled with {fallback_result.get('metadata', {}).get('fallback_strategy')}")
    
    def _cleanup_corrupted_data(self, context: Optional[Dict[str, Any]]):
        """Clean up any corrupted data (placeholder)"""
        # In a real system, this would clean up corrupted cache entries, etc.
        logger.info("Data cleanup performed")
    
    def _create_critical_error_response(self, error: Exception, start_time: datetime) -> EdgeCaseResult:
        """Create response for critical errors"""
        return EdgeCaseResult(
            case_detected=EdgeCaseType.UNKNOWN_FORMAT,
            handled=False,
            fallback_applied="critical_error_fallback",
            recovery_successful=False,
            user_message="A critical error occurred. Please try again or contact support.",
            fallback_data=self._create_minimal_fallback(),
            metadata={
                "critical_error": True,
                "error_message": str(error),
                "error_type": type(error).__name__
            },
            processing_time=(datetime.now() - start_time).total_seconds()
        )
    
    def _create_minimal_fallback(self) -> Dict[str, Any]:
        """Create minimal fallback data"""
        return {
            "preference": "mixed",
            "confidence": 0.3,
            "intensity": "low",
            "reasoning": "Emergency fallback - minimal response",
            "keywords_found": {"visual": [], "text": []},
            "specific_requests": [],
            "fallback_preference": "mixed",
            "metadata": {
                "emergency_fallback": True,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _update_statistics(self, case_info: Dict[str, Any], handling_result: Dict[str, Any]):
        """Update handling statistics"""
        self.recovery_statistics["total_edge_cases"] += 1
        
        if handling_result["recovery_successful"]:
            self.recovery_statistics["successful_recoveries"] += 1
        
        fallback_strategy = handling_result["fallback_strategy"]
        if fallback_strategy not in self.recovery_statistics["fallback_usage"]:
            self.recovery_statistics["fallback_usage"][fallback_strategy] = 0
        self.recovery_statistics["fallback_usage"][fallback_strategy] += 1
    
    def _initialize_edge_case_rules(self) -> List[EdgeCaseRule]:
        """Initialize all edge case handling rules"""
        
        return [
            # Empty input rule
            EdgeCaseRule(
                case_type=EdgeCaseType.EMPTY_INPUT,
                detection_conditions=[
                    lambda data: not data.get("input") or (isinstance(data.get("input"), str) and not data["input"].strip()),
                    lambda data: data.get("preferences") is None
                ],
                fallback_strategy=FallbackStrategy.DEFAULT_MIXED,
                priority=8,
                recovery_actions=["log_incident", "cache_fallback"],
                user_message="No preferences specified. Using balanced layout."
            ),
            
            # Malformed data rule
            EdgeCaseRule(
                case_type=EdgeCaseType.MALFORMED_DATA,
                detection_conditions=[
                    lambda data: self._is_malformed_preferences(data.get("preferences")),
                    lambda data: self._has_invalid_format(data.get("input"))
                ],
                fallback_strategy=FallbackStrategy.GRACEFUL_DEGRADATION,
                priority=9,
                recovery_actions=["cleanup_data", "log_incident"],
                user_message="Invalid data format detected. Using recovered settings."
            ),
            
            # Conflicting preferences rule
            EdgeCaseRule(
                case_type=EdgeCaseType.CONFLICTING_PREFERENCES,
                detection_conditions=[
                    lambda data: self._has_conflicting_preferences(data.get("preferences"))
                ],
                fallback_strategy=FallbackStrategy.CONTENT_ANALYSIS,
                priority=7,
                recovery_actions=["log_incident"],
                user_message="Conflicting preferences detected. Using content-based analysis."
            ),
            
            # Missing content rule
            EdgeCaseRule(
                case_type=EdgeCaseType.MISSING_CONTENT,
                detection_conditions=[
                    lambda data: self._has_missing_content(data.get("input"), data.get("context"))
                ],
                fallback_strategy=FallbackStrategy.ERROR_DISPLAY,
                priority=6,
                recovery_actions=["log_incident"],
                user_message="Some content is unavailable. Displaying what's available."
            ),
            
            # Performance degradation rule
            EdgeCaseRule(
                case_type=EdgeCaseType.PERFORMANCE_DEGRADATION,
                detection_conditions=[
                    lambda data: self._is_performance_degraded(data.get("context"))
                ],
                fallback_strategy=FallbackStrategy.MINIMAL_RESPONSE,
                priority=5,
                recovery_actions=["notify_monitoring", "log_incident"],
                user_message="Optimizing for performance. Using simplified layout."
            ),
            
            # Parsing error rule
            EdgeCaseRule(
                case_type=EdgeCaseType.PARSING_ERROR,
                detection_conditions=[
                    lambda data: self._has_parsing_errors(data.get("preferences"))
                ],
                fallback_strategy=FallbackStrategy.HISTORICAL_PREFERENCE,
                priority=8,
                recovery_actions=["log_incident", "cleanup_data"],
                user_message="Unable to parse preferences. Using previous settings or defaults."
            )
        ]
    
    # Detection condition helpers
    def _is_malformed_preferences(self, preferences: Any) -> bool:
        """Check if preferences data is malformed"""
        if not preferences:
            return False
        
        try:
            if isinstance(preferences, dict):
                # Check for required fields with invalid values
                if "preference" in preferences:
                    if preferences["preference"] not in ["visual", "text", "mixed", "unclear"]:
                        return True
                
                if "confidence" in preferences:
                    conf = preferences["confidence"]
                    if not isinstance(conf, (int, float)) or not (0 <= conf <= 1):
                        return True
                
                return False
            else:
                return True  # Preferences should be a dict
                
        except Exception:
            return True
    
    def _has_invalid_format(self, input_data: Any) -> bool:
        """Check if input data has invalid format"""
        try:
            if isinstance(input_data, str):
                # Check for obviously invalid strings
                if len(input_data) > 10000:  # Too long
                    return True
                if input_data.count('{') != input_data.count('}'):  # Unbalanced braces
                    return True
            
            return False
        except Exception:
            return True
    
    def _has_conflicting_preferences(self, preferences: Any) -> bool:
        """Check for conflicting preferences"""
        if not isinstance(preferences, dict):
            return False
        
        try:
            # Check for logical conflicts
            pref = preferences.get("preference")
            confidence = preferences.get("confidence", 0.5)
            keywords = preferences.get("keywords_found", {})
            
            if pref == "visual" and confidence > 0.7:
                # High confidence visual preference but no visual keywords
                visual_keywords = keywords.get("visual", [])
                text_keywords = keywords.get("text", [])
                if len(text_keywords) > len(visual_keywords) * 2:
                    return True
            
            if pref == "text" and confidence > 0.7:
                # High confidence text preference but no text keywords
                visual_keywords = keywords.get("visual", [])
                text_keywords = keywords.get("text", [])
                if len(visual_keywords) > len(text_keywords) * 2:
                    return True
            
            return False
            
        except Exception:
            return True
    
    def _has_missing_content(self, input_data: Any, context: Any) -> bool:
        """Check if essential content is missing"""
        try:
            if not input_data and not context:
                return True
            
            if isinstance(input_data, dict):
                # Check if all expected content fields are empty
                content_fields = ["text_response", "chart_data", "data", "summary"]
                if all(not input_data.get(field) for field in content_fields):
                    return True
            
            return False
            
        except Exception:
            return True
    
    def _is_performance_degraded(self, context: Any) -> bool:
        """Check if performance is degraded"""
        try:
            if isinstance(context, dict):
                # Check for performance indicators
                if context.get("processing_time", 0) > 5.0:  # > 5 seconds
                    return True
                if context.get("memory_usage", 0) > 100 * 1024 * 1024:  # > 100MB
                    return True
                if context.get("error_count", 0) > 3:  # Multiple errors
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _has_parsing_errors(self, preferences: Any) -> bool:
        """Check if there were parsing errors"""
        try:
            if isinstance(preferences, dict):
                metadata = preferences.get("metadata", {})
                if metadata.get("parsing_error") or metadata.get("fallback_used"):
                    return True
                
                # Check for incomplete parsing
                if preferences.get("confidence", 1.0) == 0.0:
                    return True
            
            return False
            
        except Exception:
            return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current edge case handling statistics"""
        return {
            **self.recovery_statistics,
            "rules_configured": len(self.edge_case_rules),
            "fallback_cache_size": len(self.fallback_cache),
            "performance_history_length": len(self.performance_history)
        }


# Example usage and testing
def test_edge_case_handler():
    """Test the edge case handler with various scenarios"""
    
    handler = AdvancedEdgeCaseHandler()
    
    test_cases = [
        # Empty input
        {"input": "", "preferences": None, "context": None},
        
        # Malformed preferences
        {"input": "test", "preferences": {"preference": "invalid_type", "confidence": 2.0}, "context": None},
        
        # Conflicting preferences  
        {"input": "charts graphs visual", "preferences": {"preference": "text", "confidence": 0.9, "keywords_found": {"visual": ["charts", "graphs"], "text": []}}, "context": None},
        
        # Missing content
        {"input": {}, "preferences": {"preference": "visual"}, "context": {}},
        
        # Performance degradation
        {"input": "test", "preferences": {"preference": "mixed"}, "context": {"processing_time": 10.0, "error_count": 5}}
    ]
    
    print("🔧 Testing Advanced Edge Case Handler")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        result = handler.handle_edge_cases(
            test_case["input"], 
            test_case["preferences"], 
            test_case["context"]
        )
        
        print(f"\nTest {i}:")
        print(f"Case detected: {result.case_detected.value}")
        print(f"Handled: {result.handled}")
        print(f"Fallback: {result.fallback_applied}")
        print(f"Recovery: {result.recovery_successful}")
        print(f"Message: {result.user_message}")
        print(f"Time: {result.processing_time:.3f}s")
        print("-" * 40)
    
    # Show statistics
    stats = handler.get_statistics()
    print(f"\n📊 Edge Case Statistics:")
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    test_edge_case_handler()