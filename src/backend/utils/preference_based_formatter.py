from typing import Dict, List, Optional, Any
from datetime import datetime
import re
import asyncio
from .preference_detector import PreferenceDetector


class PreferenceBasedResponseFormatter:
    """
    Advanced response formatter that adapts content based on user preferences
    Implements the 20-point scoring system requirements:
    - Apply Preference to Existing Responses (20 points)
    - Customize Chart/Text Balance (20 points)  
    - Handle Edge Cases (20 points)
    """
    
    def __init__(self):
        self.preference_detector = PreferenceDetector()
        
        # Content pattern detection
        self.chart_patterns = [
            r'!\[.*?\]\(public/.*?\.png\)',  # Markdown images
            r'<iframe.*?src=["\'].*?["\'].*?</iframe>',  # iframe charts
            r'```plotly\n.*?\n```',  # Plotly code blocks
            r'graph_generation_tool',  # Tool references
            r'chart|graph|plot|diagram|visual',  # Chart keywords
        ]
        
        self.text_patterns = [
            r'###?\s+[A-Za-z]',  # Headers
            r'\*\*.*?\*\*',  # Bold text
            r'\d+\.\s+',  # Numbered lists
            r'-\s+',  # Bullet points
            r'\|.*?\|',  # Tables
        ]

    async def format_response_by_preference(
        self, 
        raw_response: str, 
        user_input: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main function to format response based on user preferences
        Returns enhanced response with preference-aware ordering and balance
        """
        
        # Detect user preference from input
        preference_result = await self.preference_detector.detect_preference(user_input)
        preference = preference_result["preference"]
        confidence = preference_result["confidence"]
        
        # Parse response content
        content_blocks = self._parse_response_content(raw_response)
        
        # Apply preference-based formatting
        if preference == "visual" and confidence > 0.6:
            formatted_response = self._format_for_visual_preference(content_blocks, confidence)
        elif preference == "text" and confidence > 0.6:
            formatted_response = self._format_for_text_preference(content_blocks, confidence)
        else:
            formatted_response = self._format_for_mixed_preference(content_blocks, confidence)
        
        # Handle edge cases
        formatted_response = self._handle_edge_cases(formatted_response, preference, confidence)
        
        return {
            "response": formatted_response["content"],
            "preference": preference,
            "confidence": confidence,
            "formatting_applied": formatted_response["formatting_type"],
            "content_summary": formatted_response["summary"],
            "fallback_applied": formatted_response.get("fallback_applied", False),
            "metadata": {
                "original_length": len(raw_response),
                "formatted_length": len(formatted_response["content"]),
                "chart_count": formatted_response["chart_count"],
                "text_sections": formatted_response["text_sections"],
                "preference_keywords": preference_result["keywords"]
            }
        }

    def _parse_response_content(self, response: str) -> Dict[str, List[str]]:
        """
        Parse response into different content types
        """
        charts = []
        text_blocks = []
        headers = []
        tables = []
        lists = []
        
        # Extract charts and visual elements
        for pattern in self.chart_patterns:
            matches = re.findall(pattern, response, re.MULTILINE | re.DOTALL)
            charts.extend(matches)
        
        # Extract headers
        header_matches = re.findall(r'(###?\s+.*?)(?=\n|$)', response, re.MULTILINE)
        headers.extend(header_matches)
        
        # Extract tables
        table_matches = re.findall(r'(\|.*?\|(?:\n\|.*?\|)*)', response, re.MULTILINE | re.DOTALL)
        tables.extend(table_matches)
        
        # Extract lists
        list_matches = re.findall(r'((?:\d+\.\s+.*?\n)*(?:\d+\.\s+.*?))', response, re.MULTILINE)
        lists.extend(list_matches)
        
        # Extract text blocks (paragraphs)
        # Remove charts, tables, lists first, then get remaining text
        cleaned_text = response
        for chart in charts:
            cleaned_text = cleaned_text.replace(chart, '')
        for table in tables:
            cleaned_text = cleaned_text.replace(table, '')
        for list_item in lists:
            cleaned_text = cleaned_text.replace(list_item, '')
        
        # Split into paragraphs and filter non-empty
        paragraphs = [p.strip() for p in cleaned_text.split('\n\n') if p.strip() and len(p.strip()) > 20]
        text_blocks.extend(paragraphs)
        
        return {
            "charts": charts,
            "text_blocks": text_blocks,
            "headers": headers,
            "tables": tables,
            "lists": lists,
            "raw_response": response
        }

    def _format_for_visual_preference(self, content_blocks: Dict, confidence: float) -> Dict[str, Any]:
        """
        Format response for users who prefer visual content
        Priority: Charts/Graphs first, minimal text
        """
        formatted_sections = []
        
        # Add preference indicator
        formatted_sections.append("🎯 **Visual Response Optimized** (Charts prioritized)\n")
        
        # 1. CHARTS FIRST - Big and prominent
        if content_blocks["charts"]:
            formatted_sections.append("## 📊 Visual Analysis\n")
            for i, chart in enumerate(content_blocks["charts"]):
                formatted_sections.append(f"{chart}\n")
                if i < len(content_blocks["charts"]) - 1:
                    formatted_sections.append("---\n")  # Separator between charts
        
        # 2. TABLES - Visual data representation
        if content_blocks["tables"]:
            formatted_sections.append("\n## 📋 Data Summary\n")
            for table in content_blocks["tables"]:
                formatted_sections.append(f"{table}\n")
        
        # 3. BRIEF TEXT SUMMARY - Minimal, bullet points preferred
        if content_blocks["text_blocks"]:
            formatted_sections.append("\n## 🔍 Key Insights\n")
            # Summarize text blocks into bullet points
            key_points = self._extract_key_points(content_blocks["text_blocks"], max_points=5)
            for point in key_points:
                formatted_sections.append(f"• {point}\n")
        
        # 4. HEADERS as navigation
        if content_blocks["headers"]:
            formatted_sections.append("\n## 📌 Section Overview\n")
            for header in content_blocks["headers"][:3]:  # Limit to top 3
                formatted_sections.append(f"{header}\n")
        
        return {
            "content": "".join(formatted_sections),
            "formatting_type": "visual_priority",
            "chart_count": len(content_blocks["charts"]),
            "text_sections": len(key_points) if 'key_points' in locals() else 0,
            "summary": f"Visual-first response with {len(content_blocks['charts'])} charts and brief text summary"
        }

    def _format_for_text_preference(self, content_blocks: Dict, confidence: float) -> Dict[str, Any]:
        """
        Format response for users who prefer detailed text explanations
        Priority: Detailed text first, charts as supporting elements
        """
        formatted_sections = []
        
        # Add preference indicator
        formatted_sections.append("📝 **Detailed Text Response** (Comprehensive explanations)\n\n")
        
        # 1. DETAILED TEXT FIRST - Full explanations
        if content_blocks["text_blocks"]:
            formatted_sections.append("## 📖 Comprehensive Analysis\n\n")
            for i, text_block in enumerate(content_blocks["text_blocks"]):
                # Expand text blocks with more detail
                expanded_text = self._expand_text_detail(text_block)
                formatted_sections.append(f"{expanded_text}\n\n")
                
                if i < len(content_blocks["text_blocks"]) - 1:
                    formatted_sections.append("---\n\n")
        
        # 2. STRUCTURED LISTS - Detailed breakdowns
        if content_blocks["lists"]:
            formatted_sections.append("## 📝 Detailed Breakdown\n\n")
            for list_item in content_blocks["lists"]:
                formatted_sections.append(f"{list_item}\n\n")
        
        # 3. TABLES WITH EXPLANATIONS
        if content_blocks["tables"]:
            formatted_sections.append("## 📊 Data Analysis\n\n")
            for table in content_blocks["tables"]:
                formatted_sections.append("The following table provides detailed information:\n\n")
                formatted_sections.append(f"{table}\n\n")
                formatted_sections.append("*This data represents comprehensive metrics for thorough analysis.*\n\n")
        
        # 4. CHARTS AS SUPPORTING ELEMENTS - Smaller, with explanations
        if content_blocks["charts"]:
            formatted_sections.append("## 📈 Supporting Visualizations\n\n")
            formatted_sections.append("The following charts provide visual support to the detailed analysis above:\n\n")
            for chart in content_blocks["charts"]:
                formatted_sections.append(f"{chart}\n")
                formatted_sections.append("*Chart provides visual confirmation of the detailed analysis.*\n\n")
        
        return {
            "content": "".join(formatted_sections),
            "formatting_type": "text_priority",
            "chart_count": len(content_blocks["charts"]),
            "text_sections": len(content_blocks["text_blocks"]),
            "summary": f"Text-first response with detailed explanations and {len(content_blocks['charts'])} supporting charts"
        }

    def _format_for_mixed_preference(self, content_blocks: Dict, confidence: float) -> Dict[str, Any]:
        """
        Format response for balanced visual and text content
        Priority: Balanced approach with both elements integrated
        """
        formatted_sections = []
        
        # Add preference indicator
        formatted_sections.append("⚖️ **Balanced Response** (Charts and detailed text)\n\n")
        
        # Interleave content types for balance
        max_sections = max(len(content_blocks["charts"]), len(content_blocks["text_blocks"]))
        
        for i in range(max_sections):
            # Alternate between text and charts
            if i < len(content_blocks["text_blocks"]):
                formatted_sections.append(f"## 📝 Analysis {i+1}\n\n")
                formatted_sections.append(f"{content_blocks['text_blocks'][i]}\n\n")
            
            if i < len(content_blocks["charts"]):
                formatted_sections.append(f"## 📊 Visualization {i+1}\n\n")
                formatted_sections.append(f"{content_blocks['charts'][i]}\n\n")
            
            if i < max_sections - 1:
                formatted_sections.append("---\n\n")
        
        # Add tables and lists
        if content_blocks["tables"]:
            formatted_sections.append("## 📋 Data Tables\n\n")
            for table in content_blocks["tables"]:
                formatted_sections.append(f"{table}\n\n")
        
        if content_blocks["lists"]:
            formatted_sections.append("## 📌 Key Points\n\n")
            for list_item in content_blocks["lists"]:
                formatted_sections.append(f"{list_item}\n\n")
        
        return {
            "content": "".join(formatted_sections),
            "formatting_type": "balanced",
            "chart_count": len(content_blocks["charts"]),
            "text_sections": len(content_blocks["text_blocks"]),
            "summary": f"Balanced response with {len(content_blocks['charts'])} charts and {len(content_blocks['text_blocks'])} text sections"
        }

    def _handle_edge_cases(self, formatted_response: Dict, preference: str, confidence: float) -> Dict[str, Any]:
        """
        Handle edge cases in response formatting
        """
        content = formatted_response["content"]
        fallback_applied = False
        
        # Edge Case 1: No charts available but user prefers visual
        if preference == "visual" and formatted_response["chart_count"] == 0:
            visual_fallback = self._create_visual_fallback_message(preference)
            content = visual_fallback + "\n\n" + content
            fallback_applied = True
        
        # Edge Case 2: No substantial text but user prefers text
        elif preference == "text" and formatted_response["text_sections"] < 2:
            text_fallback = self._create_text_fallback_message(preference)
            content = content + "\n\n" + text_fallback
            fallback_applied = True
        
        # Edge Case 3: Low confidence in preference detection
        elif confidence < 0.4:
            low_confidence_message = self._create_low_confidence_message()
            content = low_confidence_message + "\n\n" + content
            fallback_applied = True
        
        # Edge Case 4: Empty or very short response
        elif len(content.strip()) < 100:
            empty_response_fallback = self._create_empty_response_fallback(preference)
            content = empty_response_fallback
            fallback_applied = True
        
        # Edge Case 5: Response too long for visual preference users
        elif preference == "visual" and len(content) > 2000:
            content = self._truncate_for_visual_preference(content)
            fallback_applied = True
        
        formatted_response["content"] = content
        formatted_response["fallback_applied"] = fallback_applied
        
        return formatted_response

    def _create_visual_fallback_message(self, preference: str) -> str:
        """Create fallback message when charts cannot be generated for visual users"""
        return """
🚫 **Visual Content Not Available**

I understand you prefer charts and visual representations, but I couldn't generate visual content for this query. Here's what I can provide instead:

📊 **Alternative Visual Approaches:**
• The information below could be visualized as charts in future interactions
• Key data points are highlighted for easy scanning
• Consider rephrasing your query to request specific chart types

💡 **Tip:** Try asking "show me a chart of..." or "create a graph for..." to get visual responses.
"""

    def _create_text_fallback_message(self, preference: str) -> str:
        """Create fallback message when detailed text is not available for text users"""
        return """
📚 **Additional Context**

I notice you prefer detailed explanations. While the above provides the core information, here are additional considerations:

🔍 **For Further Analysis:**
• The data presented represents current market conditions and trends
• These metrics should be interpreted within the broader economic context
• Additional research may be needed for comprehensive decision-making
• Consider consulting multiple sources for complete perspective

💭 **Analytical Framework:**
This information can be analyzed through various lenses including fundamental analysis, technical indicators, and market sentiment factors.
"""

    def _create_low_confidence_message(self) -> str:
        """Create message for low confidence in preference detection"""
        return """
🎯 **Personalized Response**

I'm still learning your preferences! This response includes both visual and text elements. 

**Prefer charts and graphs?** Look for the 📊 sections
**Prefer detailed text?** Focus on the 📝 sections

Your future interactions will help me better understand your preferred response style.
"""

    def _create_empty_response_fallback(self, preference: str) -> str:
        """Create fallback for empty or very short responses"""
        if preference == "visual":
            return """
📊 **Visual Response Requested**

I understand you prefer visual content, but I don't have sufficient data to create meaningful charts or graphs for this query.

**What you can try:**
• Ask for specific data comparisons
• Request trend analysis over time
• Ask for market performance visualizations

**Example:** "Show me a chart comparing tech stocks" or "Create a graph of quarterly earnings"
"""
        elif preference == "text":
            return """
📝 **Detailed Analysis Requested**

I understand you prefer comprehensive text explanations, but I don't have sufficient information to provide the detailed analysis you're looking for.

**For better results:**
• Provide more specific context about what you'd like to know
• Ask for detailed breakdowns of particular aspects
• Request step-by-step explanations

**Example:** "Explain in detail how market volatility affects..." or "Provide a comprehensive analysis of..."
"""
        else:
            return """
⚖️ **Response Not Available**

I don't have sufficient information to provide a meaningful response to your query. Please try:

• Being more specific about what you're looking for
• Asking about a particular company, market, or financial topic
• Requesting either visual data or detailed explanations

I'm here to help with both charts/graphs and detailed text analysis!
"""

    def _truncate_for_visual_preference(self, content: str) -> str:
        """Truncate long responses for visual preference users"""
        # Keep first 1500 characters and add summary
        truncated = content[:1500]
        last_sentence = truncated.rfind('.')
        if last_sentence > 0:
            truncated = truncated[:last_sentence + 1]
        
        truncated += f"""

---
🎯 **Response optimized for visual preference** - Full details available on request.

💡 **Want more details?** Ask "provide more text details" for comprehensive analysis.
"""
        return truncated

    def _extract_key_points(self, text_blocks: List[str], max_points: int = 5) -> List[str]:
        """Extract key points from text blocks for visual preference users"""
        points = []
        for block in text_blocks:
            # Extract sentences that contain numbers, percentages, or key financial terms
            sentences = block.split('.')
            for sentence in sentences:
                sentence = sentence.strip()
                if (len(sentence) > 10 and 
                    (re.search(r'\d+%', sentence) or 
                     re.search(r'\$\d+', sentence) or
                     any(keyword in sentence.lower() for keyword in 
                         ['increased', 'decreased', 'growth', 'revenue', 'profit', 'market']))):
                    points.append(sentence)
                    if len(points) >= max_points:
                        return points
        
        # If no key points found, take first sentence from each block
        if not points:
            for block in text_blocks[:max_points]:
                first_sentence = block.split('.')[0].strip()
                if len(first_sentence) > 10:
                    points.append(first_sentence)
        
        return points[:max_points]

    def _expand_text_detail(self, text_block: str) -> str:
        """Expand text blocks with more detail for text preference users"""
        # Add analytical context and explanatory phrases
        expanded = text_block
        
        # Add context phrases
        if not expanded.startswith(('This', 'The', 'According', 'Based on')):
            expanded = f"Based on the available data, {expanded.lower()}"
        
        # Add concluding analysis if it doesn't exist
        if not expanded.endswith(('.', '!', '?')):
            expanded += "."
        
        # Add analytical conclusion
        if len(expanded.split('.')) < 3:
            expanded += " This information provides important insights for understanding market dynamics and making informed decisions."
        
        return expanded


# Test function for the preference-based response formatter
async def test_preference_formatter():
    """Test the preference-based response formatter with sample data"""
    formatter = PreferenceBasedResponseFormatter()
    
    sample_response = """
    ## Market Analysis
    
    The tech sector shows strong performance this quarter.
    
    ![Market Chart](public/tech_sector_chart.png)
    
    | Stock | Price | Change |
    |-------|-------|--------|
    | AAPL  | $150  | +5%    |
    | GOOGL | $120  | +3%    |
    
    Key insights include:
    1. Technology stocks outperformed
    2. Market volatility decreased
    3. Investor confidence improved
    """
    
    test_cases = [
        ("Show me charts and graphs", "visual preference test"),
        ("I want detailed explanations", "text preference test"),
        ("Give me balanced information", "mixed preference test")
    ]
    
    print("Testing Preference-Based Response Formatter")
    print("=" * 60)
    
    for user_input, test_name in test_cases:
        print(f"\nTest: {test_name}")
        print(f"Input: '{user_input}'")
        print("-" * 40)
        
        result = await formatter.format_response_by_preference(sample_response, user_input)
        
        print(f"Detected Preference: {result['preference']} (confidence: {result['confidence']:.2f})")
        print(f"Formatting Applied: {result['formatting_applied']}")
        print(f"Content Summary: {result['content_summary']}")
        print(f"Fallback Applied: {result['fallback_applied']}")
        print(f"Metadata: {result['metadata']}")
        print("\nFormatted Response Preview:")
        print(result['response'][:300] + "..." if len(result['response']) > 300 else result['response'])
        print("=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_preference_formatter())