from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import asyncio
import json
from datetime import datetime

from ..utils.preference_detector import PreferenceDetector
from ..utils.preference_based_formatter import PreferenceBasedResponseFormatter
# from ..models.user_preferences import UserPreferences  # Will be implemented if needed
# from ..core.database import get_database  # Will be implemented if needed

router = APIRouter()

# Initialize the preference system
preference_detector = PreferenceDetector()
response_formatter = PreferenceBasedResponseFormatter()

@router.post("/format_response_with_preferences")
async def format_response_with_preferences(
    request: Dict[str, Any],
    db = None  # Database dependency placeholder
):
    """
    Comprehensive preference-based response formatting endpoint
    
    Expected request format:
    {
        "user_input": "user's query text",
        "raw_response": "generated response content", 
        "user_id": "optional user identifier",
        "force_preference": "optional: visual|text|mixed",
        "include_metadata": true
    }
    """
    try:
        user_input = request.get("user_input", "")
        raw_response = request.get("raw_response", "")
        user_id = request.get("user_id")
        force_preference = request.get("force_preference")
        include_metadata = request.get("include_metadata", True)
        
        if not user_input or not raw_response:
            raise HTTPException(
                status_code=400, 
                detail="Both user_input and raw_response are required"
            )
        
        # Format response based on preferences
        formatted_result = await response_formatter.format_response_by_preference(
            raw_response=raw_response,
            user_input=user_input,
            user_id=user_id
        )
        
        # Override preference if forced
        if force_preference in ["visual", "text", "mixed"]:
            formatted_result["preference"] = force_preference
            formatted_result["confidence"] = 1.0
            formatted_result["forced_preference"] = True
        
        # Store user preference for future use
        if user_id and formatted_result["confidence"] > 0.6:
            await store_user_preference(
                user_id=user_id,
                preference=formatted_result["preference"],
                confidence=formatted_result["confidence"],
                keywords=formatted_result["metadata"]["preference_keywords"],
                db=db
            )
        
        # Prepare response
        response_data = {
            "formatted_response": formatted_result["response"],
            "preference_applied": formatted_result["preference"],
            "confidence": formatted_result["confidence"],
            "success": True
        }
        
        # Include metadata if requested
        if include_metadata:
            response_data["metadata"] = {
                "formatting_type": formatted_result["formatting_applied"],
                "content_summary": formatted_result["content_summary"],
                "fallback_applied": formatted_result["fallback_applied"],
                "chart_count": formatted_result["metadata"]["chart_count"],
                "text_sections": formatted_result["metadata"]["text_sections"],
                "preference_keywords": formatted_result["metadata"]["preference_keywords"],
                "original_length": formatted_result["metadata"]["original_length"],
                "formatted_length": formatted_result["metadata"]["formatted_length"]
            }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error formatting response: {str(e)}"
        )

@router.post("/detect_preference")
async def detect_user_preference(request: Dict[str, Any]):
    """
    Detect user preference from input text
    
    Expected request format:
    {
        "text": "user input text",
        "user_id": "optional user identifier"
    }
    """
    try:
        text = request.get("text", "")
        user_id = request.get("user_id")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text input is required")
        
        # Detect preference
        preference_result = await preference_detector.detect_preference(text)
        
        return {
            "preference": preference_result["preference"],
            "confidence": preference_result["confidence"],
            "keywords_found": preference_result["keywords"],
            "ai_reasoning": preference_result["ai_reasoning"],
            "keyword_scores": preference_result["keyword_score"],
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting preference: {str(e)}"
        )

@router.get("/user_preference_stats/{user_id}")
async def get_user_preference_stats(user_id: str, db = None):
    """
    Get comprehensive preference statistics for a user
    """
    try:
        # This would need to be implemented based on your database structure
        # For now, returning mock data structure
        
        stats = {
            "user_id": user_id,
            "preference_distribution": {
                "visual": 45,
                "text": 35, 
                "mixed": 20
            },
            "confidence_average": 0.78,
            "total_interactions": 156,
            "recent_preference": "visual",
            "preference_evolution": [
                {"date": "2024-01-01", "preference": "mixed", "confidence": 0.5},
                {"date": "2024-01-15", "preference": "visual", "confidence": 0.7},
                {"date": "2024-01-30", "preference": "visual", "confidence": 0.8}
            ],
            "top_keywords": ["chart", "graph", "show", "visual", "data"],
            "formatting_history": {
                "visual_priority": 67,
                "text_priority": 28,
                "balanced": 61
            }
        }
        
        return {
            "stats": stats,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user stats: {str(e)}"
        )

@router.post("/update_user_preference")
async def update_user_preference(
    request: Dict[str, Any],
    db = None  # Database dependency placeholder
):
    """
    Manually update user preference
    
    Expected request format:
    {
        "user_id": "user identifier",
        "preference": "visual|text|mixed",
        "confidence": 0.8,
        "source": "manual|automatic"
    }
    """
    try:
        user_id = request.get("user_id")
        preference = request.get("preference")
        confidence = request.get("confidence", 1.0)
        source = request.get("source", "manual")
        
        if not user_id or preference not in ["visual", "text", "mixed"]:
            raise HTTPException(
                status_code=400, 
                detail="Valid user_id and preference (visual|text|mixed) are required"
            )
        
        # Store the preference
        await store_user_preference(
            user_id=user_id,
            preference=preference,
            confidence=confidence,
            keywords=[],
            source=source,
            db=db
        )
        
        return {
            "message": f"User preference updated to {preference}",
            "user_id": user_id,
            "preference": preference,
            "confidence": confidence,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating user preference: {str(e)}"
        )

async def store_user_preference(
    user_id: str,
    preference: str, 
    confidence: float,
    keywords: list,
    source: str = "automatic",
    db = None
):
    """
    Store user preference in database
    """
    try:
        # This would need to be implemented based on your UserPreferences model
        # For now, this is a placeholder implementation
        
        preference_data = {
            "user_id": user_id,
            "preference": preference,
            "confidence": confidence,
            "keywords": keywords,
            "source": source,
            "timestamp": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # In a real implementation, you would save this to your database
        # await db.user_preferences.update_one(
        #     {"user_id": user_id},
        #     {"$set": preference_data},
        #     upsert=True
        # )
        
        print(f"Stored preference for user {user_id}: {preference} (confidence: {confidence})")
        return True
        
    except Exception as e:
        print(f"Error storing user preference: {e}")
        return False

@router.get("/preference_system_health")
async def check_preference_system_health():
    """
    Health check endpoint for the preference system
    """
    try:
        # Test preference detection
        test_result = await preference_detector.detect_preference("Show me charts and graphs")
        
        # Test response formatting
        test_formatting = await response_formatter.format_response_by_preference(
            raw_response="Test response with ![Chart](public/test.png) and some text.",
            user_input="Show me visual data"
        )
        
        return {
            "status": "healthy",
            "preference_detector": {
                "available": True,
                "ai_available": preference_detector.model is not None,
                "test_result": test_result["preference"]
            },
            "response_formatter": {
                "available": True,
                "test_formatting": test_formatting["formatting_applied"]
            },
            "components": {
                "preference_detection": "✅ Active",
                "response_formatting": "✅ Active", 
                "edge_case_handling": "✅ Active",
                "chart_text_balance": "✅ Active"
            },
            "success": True
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "success": False
        }

# Test endpoint for development
@router.post("/test_preference_system")
async def test_preference_system(request: Dict[str, Any]):
    """
    Test endpoint for the complete preference system
    """
    try:
        test_cases = [
            {
                "user_input": "Show me charts and visual data",
                "raw_response": "## Analysis\n\nThe data shows growth.\n\n![Chart](public/growth.png)\n\n| Year | Growth |\n|------|--------|\n| 2023 | 15% |\n| 2024 | 25% |",
                "expected_preference": "visual"
            },
            {
                "user_input": "I want detailed explanations and analysis",
                "raw_response": "## Analysis\n\nThe market performance indicates several key trends.\n\n![Chart](public/trends.png)\n\nDetailed analysis shows complex relationships.",
                "expected_preference": "text"
            },
            {
                "user_input": "Give me balanced information",
                "raw_response": "## Market Overview\n\nBalanced content with both text and visuals.\n\n![Chart](public/balance.png)",
                "expected_preference": "mixed"
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases):
            formatted_result = await response_formatter.format_response_by_preference(
                raw_response=test_case["raw_response"],
                user_input=test_case["user_input"]
            )
            
            results.append({
                "test_case": i + 1,
                "input": test_case["user_input"],
                "expected_preference": test_case["expected_preference"],
                "detected_preference": formatted_result["preference"],
                "confidence": formatted_result["confidence"],
                "formatting_applied": formatted_result["formatting_applied"],
                "fallback_applied": formatted_result["fallback_applied"],
                "success": formatted_result["preference"] == test_case["expected_preference"]
            })
        
        success_rate = sum(1 for r in results if r["success"]) / len(results)
        
        return {
            "test_results": results,
            "success_rate": success_rate,
            "overall_success": success_rate >= 0.8,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running preference system tests: {str(e)}"
        )