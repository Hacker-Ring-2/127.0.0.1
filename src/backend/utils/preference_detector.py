import re
import json
import os
from typing import Dict, List, Tuple
from datetime import datetime
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_AVAILABLE = False

load_dotenv(dotenv_path=".env", override=True)

class PreferenceDetector:
    """
    Detects user preferences from text input using keyword matching and AI analysis
    """
    
    def __init__(self):
        # Configure Gemini API using existing API key
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key and GEMINI_AVAILABLE:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        elif not GEMINI_AVAILABLE:
            print("Warning: google.generativeai not available. AI-based preference detection will be disabled.")
            self.model = None
        else:
            self.model = None
            print("Warning: GEMINI_API_KEY not found, AI analysis disabled")
        
        # Define keyword categories
        self.VISUAL_KEYWORDS = {
            "primary": ["chart", "charts", "graph", "graphs", "visual", "visuals", "diagram", "diagrams", "plot", "plots"],
            "secondary": ["show", "display", "visualize", "see", "picture", "image", "graphic", "graphics"],
            "context": ["data visualization", "infographic", "dashboard", "flowchart", "timeline"]
        }
        
        self.TEXT_KEYWORDS = {
            "primary": ["text", "explain", "explanation", "explanations", "detail", "details", "description", "summary"],
            "secondary": ["tell", "describe", "elaborate", "breakdown", "analyze", "discuss"],
            "context": ["in detail", "step by step", "comprehensive", "thorough", "detailed explanation"]
        }

    def _calculate_keyword_score(self, text: str, keywords: Dict[str, List[str]]) -> Tuple[float, List[str]]:
        """Calculate preference score based on keyword matching"""
        text_lower = text.lower()
        found_keywords = []
        score = 0.0
        
        # Primary keywords (highest weight)
        for keyword in keywords["primary"]:
            if keyword in text_lower:
                found_keywords.append(keyword)
                score += 3.0
        
        # Secondary keywords (medium weight)
        for keyword in keywords["secondary"]:
            if keyword in text_lower:
                found_keywords.append(keyword)
                score += 2.0
        
        # Context keywords (lower weight)
        for phrase in keywords["context"]:
            if phrase in text_lower:
                found_keywords.append(phrase)
                score += 1.5
        
        return score, found_keywords

    async def _get_ai_analysis(self, text: str) -> Dict:
        """Use Gemini AI for semantic analysis"""
        if not self.model:
            return {"preference": "mixed", "confidence": 0.0, "reasoning": "AI analysis unavailable"}
            
        try:
            prompt = f"""
            Analyze this text and determine if the user prefers visual content (charts, graphs, diagrams) or text content (explanations, details, descriptions):
            
            Text: "{text}"
            
            Respond with only JSON in this exact format:
            {{
                "preference": "visual" or "text" or "mixed",
                "confidence": 0.0 to 1.0,
                "reasoning": "brief explanation"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse AI response
            try:
                # Clean the response text
                response_text = response.text.strip()
                # Remove markdown code blocks if present
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                elif response_text.startswith('```'):
                    response_text = response_text.replace('```', '').strip()
                
                ai_result = json.loads(response_text)
                return ai_result
            except:
                # Fallback if JSON parsing fails
                response_lower = response.text.lower()
                if "visual" in response_lower:
                    return {"preference": "visual", "confidence": 0.7, "reasoning": "AI detected visual preference"}
                elif "text" in response_lower:
                    return {"preference": "text", "confidence": 0.7, "reasoning": "AI detected text preference"}
                else:
                    return {"preference": "mixed", "confidence": 0.5, "reasoning": "AI analysis inconclusive"}
        
        except Exception as e:
            print(f"AI analysis error: {e}")
            return {"preference": "mixed", "confidence": 0.0, "reasoning": "AI analysis failed"}

    async def detect_preference(self, text: str) -> Dict:
        """
        Main function to detect user preference from input text
        Returns: { preference: "visual" | "text" | "mixed", confidence: float, keywords: List[str] }
        """
        
        # Calculate keyword scores
        visual_score, visual_keywords = self._calculate_keyword_score(text, self.VISUAL_KEYWORDS)
        text_score, text_keywords = self._calculate_keyword_score(text, self.TEXT_KEYWORDS)
        
        # Get AI analysis
        ai_analysis = await self._get_ai_analysis(text)
        
        # Combine keyword and AI analysis
        keyword_preference = "mixed"
        keyword_confidence = 0.0
        found_keywords = []
        
        if visual_score > text_score:
            keyword_preference = "visual"
            keyword_confidence = min(visual_score / 10.0, 1.0)  # Normalize to 0-1
            found_keywords = visual_keywords
        elif text_score > visual_score:
            keyword_preference = "text"
            keyword_confidence = min(text_score / 10.0, 1.0)
            found_keywords = text_keywords
        else:
            keyword_preference = "mixed"
            keyword_confidence = 0.5
            found_keywords = visual_keywords + text_keywords
        
        # Final decision combining both methods
        if keyword_confidence > 0.7:
            # High confidence in keyword matching
            final_preference = keyword_preference
            final_confidence = keyword_confidence
        elif ai_analysis["confidence"] > 0.7:
            # High confidence in AI analysis
            final_preference = ai_analysis["preference"]
            final_confidence = ai_analysis["confidence"]
        elif keyword_preference == ai_analysis["preference"]:
            # Both methods agree
            final_preference = keyword_preference
            final_confidence = (keyword_confidence + ai_analysis["confidence"]) / 2
        else:
            # Methods disagree, use mixed
            final_preference = "mixed"
            final_confidence = 0.5
        
        return {
            "preference": final_preference,
            "confidence": final_confidence,
            "keywords": found_keywords,
            "ai_reasoning": ai_analysis.get("reasoning", ""),
            "keyword_score": {"visual": visual_score, "text": text_score}
        }

# Test function
async def test_preference_detector():
    detector = PreferenceDetector()
    
    test_cases = [
        "I prefer charts and graphs",
        "Give me detailed text explanations", 
        "Show me visual data with graphs",
        "Explain in detail with comprehensive text",
        "I want to see diagrams and charts",
        "Provide thorough descriptions and analysis"
    ]
    
    print("Testing Preference Detector:")
    print("=" * 50)
    
    for text in test_cases:
        result = await detector.detect_preference(text)
        print(f"Input: '{text}'")
        print(f"Result: {result}")
        print("-" * 50)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_preference_detector())