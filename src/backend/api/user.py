from http.client import HTTPException
from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from src.backend.db import mongodb
from src.backend.core.api_limit import apiSecurityFree
from src.backend.models.app_io_schemas import Onboarding, OnboardingRequest
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

router = APIRouter()

@router.patch("/user")
async def update_user(user: apiSecurityFree, request: mongodb.UpdateUserRequest):

    for key,value in request.model_dump().items() :
        if value :
            user._set_attr(key,value)
        
    await user.save()
    return user


@router.get("/personalization_info")
async def get_user_personalization(user: apiSecurityFree):
    personalization = await mongodb.get_personalization(user.id.__str__())
    if not personalization:
        raise HTTPException(status_code=200, detail="Please take a moment to set up your preferences to enhance your experience.")
    return personalization

@router.post("/personalization")
async def update_user_personalization(user: apiSecurityFree, request: mongodb.PersonalizationRequest):
    updated = await mongodb.create_or_update_personalization(user.id.__str__(), request.dict(exclude_unset=True))
    return updated

@router.delete("/user/{user_id}")
async def delete_user_endpoint(user_id: str):
    try:
        # Use the cascading delete service function
        result = await mongodb.delete_user(user_id)
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404 User not found)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error occurred while deleting user: {str(e)}"
        )
     
@router.get("/is_new_user")
async def is_new_user(token: Annotated[str, Depends(oauth2_scheme)]):
    return await mongodb.is_new_user_token(token)
@router.post("/onboarding", response_model=Onboarding)
async def update_onboarding(user: apiSecurityFree, request: OnboardingRequest):
    try:
        updated = await mongodb.create_or_update_onboarding(user.id.__str__(), request.dict(exclude_unset=True))
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/get_user_info")
async def user_by_id(user: apiSecurityFree):
    return user.to_dict()


@router.post("/update_personalization")
async def update_user_personalization_preferences(user: apiSecurityFree, request: dict):
    """Update user preferences based on text input analysis"""
    try:
        # Import here to avoid circular imports
        from src.backend.utils.preference_detector import PreferenceDetector
        from src.backend.models.model import UserPreferences, PersonalizationLog
        
        input_text = request.get("input_text", "")
        session_id = request.get("session_id", "")
        message_id = request.get("message_id", "")
        
        if not input_text:
            raise HTTPException(status_code=400, detail="input_text is required")
        
        # Detect preference from input text
        detector = PreferenceDetector()
        detection_result = await detector.detect_preference(input_text)
        
        # Update or create user preferences
        user_preferences = await UserPreferences.find_one(UserPreferences.user_id == user.id)
        
        if user_preferences:
            # Update existing preferences
            user_preferences.preferred_response_type = detection_result["preference"]
            user_preferences.confidence_score = detection_result["confidence"]
            user_preferences.last_detection_text = input_text
            user_preferences.detection_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "preference": detection_result["preference"],
                "confidence": detection_result["confidence"],
                "keywords": detection_result["keywords"]
            })
            user_preferences.updated_at = datetime.now(timezone.utc)
            await user_preferences.save()
        else:
            # Create new preferences
            user_preferences = UserPreferences(
                user_id=user.id,
                preferred_response_type=detection_result["preference"],
                confidence_score=detection_result["confidence"],
                last_detection_text=input_text,
                detection_history=[{
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "preference": detection_result["preference"],
                    "confidence": detection_result["confidence"],
                    "keywords": detection_result["keywords"]
                }]
            )
            await user_preferences.insert()
        
        # Log the personalization event
        personalization_log = PersonalizationLog(
            user_id=user.id,
            session_id=session_id,
            message_id=message_id,
            input_text=input_text,
            detected_preference=detection_result["preference"],
            confidence_score=detection_result["confidence"],
            keywords_found=detection_result["keywords"],
            ai_reasoning=detection_result.get("ai_reasoning", ""),
            keyword_scores=detection_result.get("keyword_score", {})
        )
        await personalization_log.insert()
        
        return {
            "preference": detection_result["preference"],
            "confidence": detection_result["confidence"],
            "message": "Preferences updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating personalization: {str(e)}")


@router.get("/get_user_preferences")
async def get_user_preferences(user: apiSecurityFree):
    """Get current user preferences"""
    try:
        from src.backend.models.model import UserPreferences
        
        user_preferences = await UserPreferences.find_one(UserPreferences.user_id == user.id)
        
        if not user_preferences:
            return {
                "preference": "mixed",
                "confidence": 0.0,
                "message": "No preferences set yet"
            }
        
        return {
            "preference": user_preferences.preferred_response_type,
            "confidence": user_preferences.confidence_score,
            "last_updated": user_preferences.updated_at.isoformat(),
            "detection_count": len(user_preferences.detection_history)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting preferences: {str(e)}")
