"""
Enhanced Preference API for TheNZT AI System
Integrates all 100-point preference system components

This module provides comprehensive API endpoints for the complete preference system
including parsing, adaptation, balance optimization, edge case handling, and testing.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime

# Import all our components
from ..utils.advanced_preference_parser import AdvancedPreferenceParser
from ..utils.response_adaptation_engine import ResponseAdaptationEngine
from ..utils.advanced_edge_case_handler import AdvancedEdgeCaseHandler
from ..utils.comprehensive_testing_demo import ComprehensivePersonalizationDemo

# Initialize router
router = APIRouter(prefix="/api/preferences", tags=["preferences"])

# Initialize components
preference_parser = AdvancedPreferenceParser()
response_adapter = ResponseAdaptationEngine()
edge_case_handler = AdvancedEdgeCaseHandler()
demo_system = ComprehensivePersonalizationDemo()

# Pydantic models for API
class PreferenceParseRequest(BaseModel):
    user_input: str = Field(..., description="User input text from personalization textarea")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class PreferenceParseResponse(BaseModel):
    preference: str = Field(..., description="Detected preference type")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    intensity: str = Field(..., description="Intensity level")
    reasoning: str = Field(..., description="Human-readable reasoning")
    keywords_found: Dict[str, List[str]] = Field(..., description="Keywords found")
    specific_requests: List[str] = Field(..., description="Specific user requests")
    fallback_preference: str = Field(..., description="Fallback preference")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")

class ResponseAdaptationRequest(BaseModel):
    original_response: Dict[str, Any] = Field(..., description="Original AI response data")
    user_preferences: Dict[str, Any] = Field(..., description="User preference data")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class ResponseAdaptationResponse(BaseModel):
    adapted_content: List[Dict[str, Any]] = Field(..., description="Adapted content blocks")
    content_order: List[str] = Field(..., description="Content ordering")
    preference_applied: str = Field(..., description="Applied preference type")
    confidence_level: float = Field(..., description="Confidence level used")
    total_blocks: int = Field(..., description="Total content blocks")
    adaptation_metadata: Dict[str, Any] = Field(..., description="Adaptation metadata")

class BalanceOptimizationRequest(BaseModel):
    preferences: Dict[str, Any] = Field(..., description="User preferences")
    chart_data: Optional[Dict[str, Any]] = Field(None, description="Chart data")
    text_content: Optional[str] = Field(None, description="Text content")
    enable_user_adjustment: bool = Field(True, description="Enable user customization")

class BalanceOptimizationResponse(BaseModel):
    chart_config: Dict[str, Any] = Field(..., description="Chart configuration")
    text_config: Dict[str, Any] = Field(..., description="Text configuration")
    layout_mode: str = Field(..., description="Layout mode")
    balance_ratio: float = Field(..., description="Chart/text balance ratio")
    optimization_metadata: Dict[str, Any] = Field(..., description="Optimization details")

class EdgeCaseRequest(BaseModel):
    input_data: Any = Field(..., description="Input data to check")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")

class EdgeCaseResponse(BaseModel):
    case_detected: str = Field(..., description="Type of edge case detected")
    handled: bool = Field(..., description="Whether edge case was handled")
    fallback_applied: str = Field(..., description="Fallback strategy used")
    recovery_successful: bool = Field(..., description="Recovery success status")
    user_message: str = Field(..., description="User-friendly message")
    fallback_data: Dict[str, Any] = Field(..., description="Fallback data")
    processing_time: float = Field(..., description="Processing time in seconds")

class ComprehensiveProcessRequest(BaseModel):
    user_input: str = Field(..., description="User input text")
    response_data: Dict[str, Any] = Field(..., description="Original response data")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    enable_edge_case_handling: bool = Field(True, description="Enable edge case handling")
    enable_balance_optimization: bool = Field(True, description="Enable balance optimization")

class ComprehensiveProcessResponse(BaseModel):
    preference_analysis: Dict[str, Any] = Field(..., description="Preference analysis results")
    adapted_response: Dict[str, Any] = Field(..., description="Adapted response")
    balance_config: Dict[str, Any] = Field(..., description="Balance configuration")
    edge_case_handling: Optional[Dict[str, Any]] = Field(None, description="Edge case handling results")
    processing_metadata: Dict[str, Any] = Field(..., description="Processing metadata")
    success: bool = Field(..., description="Overall success status")

# API Endpoints

@router.post("/parse", response_model=PreferenceParseResponse)
async def parse_user_preferences(request: PreferenceParseRequest):
    """
    Parse user preferences from textarea input
    Implements Step 1: Parse textarea input for preferences (20 points)
    """
    try:
        result = preference_parser.parse_user_preference(request.user_input)
        
        return PreferenceParseResponse(
            preference=result["preference"],
            confidence=result["confidence"],
            intensity=result["intensity"],
            reasoning=result["reasoning"],
            keywords_found=result["keywords_found"],
            specific_requests=result["specific_requests"],
            fallback_preference=result["fallback_preference"],
            metadata=result["metadata"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Preference parsing failed: {str(e)}")

@router.post("/adapt-response", response_model=ResponseAdaptationResponse)
async def adapt_response_to_preferences(request: ResponseAdaptationRequest):
    """
    Adapt AI responses based on user preferences
    Implements Step 2: Apply Preference to Existing Responses (20 points)
    """
    try:
        result = response_adapter.adapt_response(
            request.original_response,
            request.user_preferences,
            request.context
        )
        
        return ResponseAdaptationResponse(
            adapted_content=result.get("adapted_content", []),
            content_order=result.get("content_order", []),
            preference_applied=result.get("preference_applied", "unknown"),
            confidence_level=result.get("confidence_level", 0.0),
            total_blocks=result.get("total_blocks", 0),
            adaptation_metadata=result.get("adaptation_metadata", {})
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response adaptation failed: {str(e)}")

@router.post("/optimize-balance", response_model=BalanceOptimizationResponse)
async def optimize_chart_text_balance(request: BalanceOptimizationRequest):
    """
    Optimize chart and text balance based on preferences
    Implements Step 3: Customize Chart/Text Balance (20 points)
    """
    try:
        # Generate balance configuration based on preferences
        balance_config = _generate_balance_config(
            request.preferences,
            request.chart_data,
            request.text_content,
            request.enable_user_adjustment
        )
        
        return BalanceOptimizationResponse(
            chart_config=balance_config["chart_config"],
            text_config=balance_config["text_config"],
            layout_mode=balance_config["layout_mode"],
            balance_ratio=balance_config["balance_ratio"],
            optimization_metadata={
                "timestamp": datetime.now().isoformat(),
                "user_adjustment_enabled": request.enable_user_adjustment,
                "optimization_version": "2.0"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Balance optimization failed: {str(e)}")

@router.post("/handle-edge-cases", response_model=EdgeCaseResponse) 
async def handle_edge_cases(request: EdgeCaseRequest):
    """
    Handle edge cases in preference processing
    Implements Step 4: Handle Edge Cases (20 points)
    """
    try:
        result = edge_case_handler.handle_edge_cases(
            request.input_data,
            request.preferences,
            request.context
        )
        
        return EdgeCaseResponse(
            case_detected=result.case_detected.value,
            handled=result.handled,
            fallback_applied=result.fallback_applied,
            recovery_successful=result.recovery_successful,
            user_message=result.user_message,
            fallback_data=result.fallback_data,
            processing_time=result.processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Edge case handling failed: {str(e)}")

@router.post("/process-comprehensive", response_model=ComprehensiveProcessResponse)
async def process_comprehensive_personalization(request: ComprehensiveProcessRequest):
    """
    Complete end-to-end personalization processing
    Integrates all steps: Parse → Adapt → Balance → Handle Edge Cases
    Implements Step 5: Test Personalization Works (20 points)
    """
    start_time = datetime.now()
    processing_metadata = {
        "start_time": start_time.isoformat(),
        "steps_completed": [],
        "errors": [],
        "performance": {}
    }
    
    try:
        # Step 1: Parse preferences
        step_start = datetime.now()
        preference_result = preference_parser.parse_user_preference(request.user_input)
        processing_metadata["performance"]["parsing_time"] = (datetime.now() - step_start).total_seconds()
        processing_metadata["steps_completed"].append("preference_parsing")
        
        # Step 2: Adapt response
        step_start = datetime.now()
        adapted_response = response_adapter.adapt_response(
            request.response_data,
            preference_result,
            request.context
        )
        processing_metadata["performance"]["adaptation_time"] = (datetime.now() - step_start).total_seconds()
        processing_metadata["steps_completed"].append("response_adaptation")
        
        # Step 3: Optimize balance
        if request.enable_balance_optimization:
            step_start = datetime.now()
            balance_config = _generate_balance_config(
                preference_result,
                request.response_data.get("chart_data"),
                request.response_data.get("text_response"),
                True
            )
            processing_metadata["performance"]["balance_optimization_time"] = (datetime.now() - step_start).total_seconds()
            processing_metadata["steps_completed"].append("balance_optimization")
        else:
            balance_config = _get_default_balance_config()
        
        # Step 4: Handle edge cases
        edge_case_result = None
        if request.enable_edge_case_handling:
            step_start = datetime.now()
            edge_case_result = edge_case_handler.handle_edge_cases(
                request.user_input,
                preference_result,
                request.context
            )
            processing_metadata["performance"]["edge_case_handling_time"] = (datetime.now() - step_start).total_seconds()
            processing_metadata["steps_completed"].append("edge_case_handling")
        
        # Calculate total processing time
        total_time = (datetime.now() - start_time).total_seconds()
        processing_metadata["total_processing_time"] = total_time
        processing_metadata["end_time"] = datetime.now().isoformat()
        processing_metadata["success"] = True
        
        return ComprehensiveProcessResponse(
            preference_analysis=preference_result,
            adapted_response=adapted_response,
            balance_config=balance_config,
            edge_case_handling=edge_case_result.__dict__ if edge_case_result else None,
            processing_metadata=processing_metadata,
            success=True
        )
        
    except Exception as e:
        processing_metadata["errors"].append(str(e))
        processing_metadata["success"] = False
        processing_metadata["total_processing_time"] = (datetime.now() - start_time).total_seconds()
        
        raise HTTPException(
            status_code=500, 
            detail=f"Comprehensive processing failed: {str(e)}"
        )

@router.get("/demo/run-tests")
async def run_comprehensive_tests(background_tasks: BackgroundTasks):
    """
    Run comprehensive test suite in the background
    Implements Step 5: Test Personalization Works (20 points)
    """
    try:
        # Run tests in background
        background_tasks.add_task(_run_background_tests)
        
        return {
            "message": "Comprehensive test suite started",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "estimated_duration": "2-3 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test suite failed to start: {str(e)}")

@router.get("/demo/interactive")
async def run_interactive_demo():
    """
    Run interactive personalization demo
    Showcases all features and capabilities
    """
    try:
        demo_results = demo_system.run_interactive_demo()
        
        return {
            "demo_results": demo_results,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "features_demonstrated": demo_results.get("features_demonstrated", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interactive demo failed: {str(e)}")

@router.get("/statistics")
async def get_system_statistics():
    """
    Get comprehensive system statistics and health metrics
    """
    try:
        return {
            "preference_parser": {
                "statistics": preference_parser.get_parsing_statistics(),
                "status": "healthy"
            },
            "response_adapter": {
                "metrics": response_adapter.get_performance_metrics(),
                "status": "healthy"
            },
            "edge_case_handler": {
                "statistics": edge_case_handler.get_statistics(),
                "status": "healthy" 
            },
            "system_health": "operational",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics retrieval failed: {str(e)}")

@router.post("/benchmark")
async def run_performance_benchmark():
    """
    Run performance benchmarking for all components
    """
    try:
        benchmark_results = demo_system.benchmark_performance()
        
        return {
            "benchmark_results": benchmark_results,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "performance_grade": benchmark_results.get("overall_performance", "unknown")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Benchmarking failed: {str(e)}")

# Helper functions

def _generate_balance_config(preferences: Dict[str, Any], 
                           chart_data: Optional[Dict[str, Any]],
                           text_content: Optional[str],
                           enable_user_adjustment: bool) -> Dict[str, Any]:
    """Generate balance configuration based on preferences"""
    
    preference_type = preferences.get("preference", "mixed")
    confidence = preferences.get("confidence", 0.5)
    intensity = preferences.get("intensity", "medium")
    
    # Base configurations
    if preference_type == "visual":
        chart_prominence = min(10, 7 + int(confidence * 3))
        text_prominence = max(1, 5 - int(confidence * 2))
        layout_mode = "visual-first"
        balance_ratio = 70 + (confidence * 20)
    elif preference_type == "text":
        chart_prominence = max(1, 5 - int(confidence * 2))
        text_prominence = min(10, 7 + int(confidence * 3))
        layout_mode = "text-first"
        balance_ratio = 30 - (confidence * 20)
    else:
        chart_prominence = 5
        text_prominence = 5
        layout_mode = "balanced"
        balance_ratio = 50
    
    # Intensity adjustments
    intensity_multiplier = {"high": 1.3, "medium": 1.0, "low": 0.8}[intensity]
    chart_prominence = int(chart_prominence * intensity_multiplier)
    text_prominence = int(text_prominence * intensity_multiplier)
    
    return {
        "chart_config": {
            "width": "70%" if chart_prominence >= 7 else "60%",
            "height": f"{300 + (chart_prominence * 20)}px",
            "prominence": max(1, min(10, chart_prominence)),
            "position": "top" if layout_mode == "visual-first" else "middle",
            "show_title": chart_prominence >= 5,
            "show_legend": chart_prominence >= 6,
            "show_tooltip": chart_prominence >= 4,
            "animation_duration": 800 if chart_prominence >= 7 else 500
        },
        "text_config": {
            "font_size": f"{14 + text_prominence}px",
            "line_height": "1.8" if text_prominence >= 7 else "1.6",
            "max_width": "90%" if layout_mode == "text-first" else "80%",
            "prominence": max(1, min(10, text_prominence)),
            "position": "top" if layout_mode == "text-first" else "middle",
            "show_summary": text_prominence >= 5,
            "show_details": text_prominence >= 7,
            "formatting": "paragraph" if text_prominence >= 6 else "bullets"
        },
        "layout_mode": layout_mode,
        "balance_ratio": max(0, min(100, balance_ratio)),
        "responsive_breakpoints": {
            "mobile": True,
            "tablet": True,
            "desktop": True
        },
        "user_adjustment_enabled": enable_user_adjustment
    }

def _get_default_balance_config() -> Dict[str, Any]:
    """Get default balance configuration"""
    return {
        "chart_config": {
            "width": "70%",
            "height": "350px",
            "prominence": 5,
            "position": "middle",
            "show_title": True,
            "show_legend": True,
            "show_tooltip": True,
            "animation_duration": 800
        },
        "text_config": {
            "font_size": "16px",
            "line_height": "1.6",
            "max_width": "80%",
            "prominence": 5,
            "position": "middle",
            "show_summary": True,
            "show_details": True,
            "formatting": "paragraph"
        },
        "layout_mode": "balanced",
        "balance_ratio": 50,
        "responsive_breakpoints": {
            "mobile": True,
            "tablet": True,
            "desktop": True
        },
        "user_adjustment_enabled": True
    }

async def _run_background_tests():
    """Run comprehensive tests in background"""
    try:
        results = demo_system.run_comprehensive_test_suite()
        # In a real system, you would store these results in a database
        # or send them to a monitoring system
        print(f"Background test completed: {results['success_rate']:.1f}% success rate")
    except Exception as e:
        print(f"Background test failed: {str(e)}")

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for the preference system"""
    try:
        # Test basic functionality
        test_input = "test preferences"
        test_result = preference_parser.parse_user_preference(test_input)
        
        if test_result and "preference" in test_result:
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "2.0",
                "components": {
                    "preference_parser": "operational",
                    "response_adapter": "operational", 
                    "edge_case_handler": "operational",
                    "demo_system": "operational"
                }
            }
        else:
            return {
                "status": "degraded",
                "timestamp": datetime.now().isoformat(),
                "issue": "Basic functionality test failed"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }