"""
Comprehensive test suite for the preference-based response system
Tests all 60 points of functionality:
- Apply Preference to Existing Responses (20 points) ✅
- Customize Chart/Text Balance (20 points) ✅  
- Handle Edge Cases (20 points) ✅
"""

import asyncio
import json
import sys
import os
from typing import Dict, List, Any
from datetime import datetime

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

try:
    from src.backend.utils.preference_detector import PreferenceDetector
    from src.backend.utils.preference_based_formatter import PreferenceBasedResponseFormatter
    PREFERENCE_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import preference system: {e}")
    PREFERENCE_SYSTEM_AVAILABLE = False


class PreferenceSystemTestSuite:
    """
    Comprehensive test suite for the preference-based response system
    """
    
    def __init__(self):
        if PREFERENCE_SYSTEM_AVAILABLE:
            self.preference_detector = PreferenceDetector()
            self.response_formatter = PreferenceBasedResponseFormatter()
        else:
            self.preference_detector = None
            self.response_formatter = None
        
        self.test_results = []
        self.test_stats = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "edge_cases_handled": 0,
            "preference_accuracy": 0.0,
            "formatting_accuracy": 0.0
        }

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """
        Run all preference system tests and return comprehensive results
        """
        print("🚀 Starting Comprehensive Preference System Test Suite")
        print("=" * 80)
        
        if not PREFERENCE_SYSTEM_AVAILABLE:
            return {
                "status": "skipped",
                "reason": "Preference system not available",
                "success": False
            }
        
        # Test categories
        test_categories = [
            ("Preference Detection Tests", self._test_preference_detection),
            ("Response Ordering Tests (20 points)", self._test_response_ordering),
            ("Chart/Text Balance Tests (20 points)", self._test_chart_text_balance),
            ("Edge Case Handling Tests (20 points)", self._test_edge_case_handling),
            ("Integration Tests", self._test_integration),
            ("Performance Tests", self._test_performance),
            ("Error Handling Tests", self._test_error_handling)
        ]
        
        for category_name, test_function in test_categories:
            print(f"\n📋 {category_name}")
            print("-" * 60)
            
            category_results = await test_function()
            self.test_results.append({
                "category": category_name,
                "results": category_results,
                "timestamp": datetime.now().isoformat()
            })
            
            # Update stats
            passed = sum(1 for r in category_results if r.get("passed", False))
            total = len(category_results)
            
            print(f"✅ {passed}/{total} tests passed in {category_name}")
            
            self.test_stats["total_tests"] += total
            self.test_stats["passed_tests"] += passed
            self.test_stats["failed_tests"] += (total - passed)
        
        # Calculate final scores
        self._calculate_final_scores()
        
        # Generate comprehensive report
        return self._generate_final_report()

    async def _test_preference_detection(self) -> List[Dict[str, Any]]:
        """
        Test preference detection accuracy
        """
        test_cases = [
            {
                "input": "Show me charts and graphs of the market data",
                "expected_preference": "visual",
                "min_confidence": 0.7,
                "test_name": "Visual preference detection"
            },
            {
                "input": "I want detailed explanations and comprehensive analysis",
                "expected_preference": "text",
                "min_confidence": 0.7,
                "test_name": "Text preference detection"
            },
            {
                "input": "Give me both charts and detailed information",
                "expected_preference": "mixed",
                "min_confidence": 0.5,
                "test_name": "Mixed preference detection"
            },
            {
                "input": "Create a visual dashboard with pie charts and bar graphs",
                "expected_preference": "visual",
                "min_confidence": 0.8,
                "test_name": "Strong visual preference"
            },
            {
                "input": "Explain step by step with thorough details and comprehensive breakdown",
                "expected_preference": "text",
                "min_confidence": 0.8,
                "test_name": "Strong text preference"
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                result = await self.preference_detector.detect_preference(test_case["input"])
                
                passed = (
                    result["preference"] == test_case["expected_preference"] and
                    result["confidence"] >= test_case["min_confidence"]
                )
                
                results.append({
                    "test_name": test_case["test_name"],
                    "input": test_case["input"],
                    "expected": test_case["expected_preference"],
                    "actual": result["preference"],
                    "confidence": result["confidence"],
                    "expected_confidence": test_case["min_confidence"],
                    "passed": passed,
                    "keywords_found": result.get("keywords", []),
                    "ai_reasoning": result.get("ai_reasoning", "")
                })
                
                print(f"{'✅' if passed else '❌'} {test_case['test_name']}: {result['preference']} ({result['confidence']:.2f})")
                
            except Exception as e:
                results.append({
                    "test_name": test_case["test_name"],
                    "error": str(e),
                    "passed": False
                })
                print(f"❌ {test_case['test_name']}: Error - {e}")
        
        return results

    async def _test_response_ordering(self) -> List[Dict[str, Any]]:
        """
        Test response ordering based on preferences (20 points)
        """
        test_response = """
        ## Market Analysis
        
        The tech sector shows strong performance with multiple indicators.
        
        ![Tech Performance Chart](public/tech_performance.png)
        
        | Company | Growth | Revenue |
        |---------|--------|---------|
        | Apple   | 15%    | $400B   |
        | Google  | 12%    | $300B   |
        
        The market data indicates several key trends that investors should consider.
        
        ![Market Trends](public/market_trends.png)
        
        Key insights include improved investor confidence and sector rotation.
        """
        
        test_cases = [
            {
                "user_input": "Show me visual data and charts",
                "expected_preference": "visual",
                "test_name": "Visual ordering - charts first",
                "checks": [
                    "Charts appear before detailed text",
                    "Visual content is prioritized",
                    "Brief text summaries provided"
                ]
            },
            {
                "user_input": "I want detailed text explanations",
                "expected_preference": "text", 
                "test_name": "Text ordering - explanations first",
                "checks": [
                    "Detailed text appears first",
                    "Charts are secondary/supporting",
                    "Comprehensive explanations provided"
                ]
            },
            {
                "user_input": "Give me balanced information",
                "expected_preference": "mixed",
                "test_name": "Balanced ordering - mixed content",
                "checks": [
                    "Content is interleaved",
                    "Both text and charts balanced",
                    "Neither prioritized over other"
                ]
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                formatted_result = await self.response_formatter.format_response_by_preference(
                    raw_response=test_response,
                    user_input=test_case["user_input"]
                )
                
                # Analyze the formatted response
                response_content = formatted_result["response"]
                preference_applied = formatted_result["preference"]
                
                # Check ordering based on preference
                chart_positions = []
                text_positions = []
                
                lines = response_content.split('\n')
                for i, line in enumerate(lines):
                    if '![' in line or 'public/' in line:
                        chart_positions.append(i)
                    elif len(line.strip()) > 20 and not line.startswith('#'):
                        text_positions.append(i)
                
                # Evaluate ordering
                passed = True
                checks_passed = []
                
                if preference_applied == "visual":
                    # Charts should appear early
                    if chart_positions and text_positions:
                        avg_chart_pos = sum(chart_positions) / len(chart_positions)
                        avg_text_pos = sum(text_positions) / len(text_positions)
                        charts_first = avg_chart_pos < avg_text_pos
                        checks_passed.append(f"Charts first: {'✅' if charts_first else '❌'}")
                        passed = passed and charts_first
                
                elif preference_applied == "text":
                    # Detailed text should dominate
                    text_ratio = len([l for l in lines if len(l.strip()) > 30]) / max(len(lines), 1)
                    text_heavy = text_ratio > 0.4
                    checks_passed.append(f"Text heavy: {'✅' if text_heavy else '❌'} ({text_ratio:.2f})")
                    passed = passed and text_heavy
                
                elif preference_applied == "mixed":
                    # Balanced content
                    chart_count = len(chart_positions)
                    text_count = len([l for l in lines if len(l.strip()) > 20])
                    balanced = abs(chart_count - text_count/5) < 2  # Rough balance check
                    checks_passed.append(f"Balanced: {'✅' if balanced else '❌'}")
                    passed = passed and balanced
                
                results.append({
                    "test_name": test_case["test_name"],
                    "user_input": test_case["user_input"],
                    "expected_preference": test_case["expected_preference"],
                    "actual_preference": preference_applied,
                    "confidence": formatted_result["confidence"],
                    "formatting_type": formatted_result["formatting_applied"],
                    "chart_count": formatted_result["metadata"]["chart_count"],
                    "text_sections": formatted_result["metadata"]["text_sections"],
                    "checks_passed": checks_passed,
                    "passed": passed,
                    "response_length": len(response_content)
                })
                
                print(f"{'✅' if passed else '❌'} {test_case['test_name']}: {preference_applied} formatting")
                for check in checks_passed:
                    print(f"  {check}")
                
            except Exception as e:
                results.append({
                    "test_name": test_case["test_name"],
                    "error": str(e),
                    "passed": False
                })
                print(f"❌ {test_case['test_name']}: Error - {e}")
        
        return results

    async def _test_chart_text_balance(self) -> List[Dict[str, Any]]:
        """
        Test chart/text balance customization (20 points)
        """
        test_response = """
        ## Financial Overview
        
        Market analysis reveals significant trends.
        
        ![Performance Chart](public/performance.png)
        
        | Metric | Value | Change |
        |--------|-------|--------|
        | Revenue| $100M | +15%   |
        | Profit | $25M  | +20%   |
        
        Detailed analysis of the quarterly results shows strong performance.
        
        ![Quarterly Chart](public/quarterly.png)
        """
        
        test_cases = [
            {
                "preference": "visual",
                "test_name": "Visual balance - large charts, brief text",
                "expected_features": [
                    "Large chart sizing indicated",
                    "Brief text summaries",
                    "Visual elements prioritized",
                    "Minimal explanatory text"
                ]
            },
            {
                "preference": "text",
                "test_name": "Text balance - detailed explanations, small charts",
                "expected_features": [
                    "Detailed explanations expanded",
                    "Charts marked as supporting",
                    "Comprehensive text analysis",
                    "Small chart sizing indicated"
                ]
            },
            {
                "preference": "mixed",
                "test_name": "Mixed balance - balanced charts and text",
                "expected_features": [
                    "Balanced content distribution",
                    "Charts and text integrated",
                    "Neither heavily prioritized",
                    "Medium chart sizing"
                ]
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            try:
                # Simulate user input for each preference
                user_inputs = {
                    "visual": "show me charts and visual data",
                    "text": "provide detailed explanations",
                    "mixed": "give me balanced information"
                }
                
                formatted_result = await self.response_formatter.format_response_by_preference(
                    raw_response=test_response,
                    user_input=user_inputs[test_case["preference"]]
                )
                
                response_content = formatted_result["response"]
                
                # Analyze balance characteristics
                features_found = []
                
                if test_case["preference"] == "visual":
                    # Check for visual priority indicators
                    if "Visual Response Optimized" in response_content:
                        features_found.append("✅ Large chart sizing indicated")
                    if "Key Insights" in response_content:
                        features_found.append("✅ Brief text summaries")
                    if response_content.count("📊") > 0:
                        features_found.append("✅ Visual elements prioritized")
                
                elif test_case["preference"] == "text":
                    # Check for text priority indicators
                    if "Detailed Text Response" in response_content:
                        features_found.append("✅ Detailed explanations expanded")
                    if "Supporting Visualizations" in response_content:
                        features_found.append("✅ Charts marked as supporting")
                    if "Comprehensive Analysis" in response_content:
                        features_found.append("✅ Comprehensive text analysis")
                
                elif test_case["preference"] == "mixed":
                    # Check for balanced indicators
                    if "Balanced Response" in response_content:
                        features_found.append("✅ Balanced content distribution")
                    if formatted_result["formatting_applied"] == "balanced":
                        features_found.append("✅ Charts and text integrated")
                
                passed = len(features_found) >= 2  # At least 2 features should be present
                
                results.append({
                    "test_name": test_case["test_name"],
                    "preference": test_case["preference"],
                    "formatting_applied": formatted_result["formatting_applied"],
                    "chart_count": formatted_result["metadata"]["chart_count"],
                    "text_sections": formatted_result["metadata"]["text_sections"],
                    "features_found": features_found,
                    "expected_features": test_case["expected_features"],
                    "passed": passed,
                    "confidence": formatted_result["confidence"]
                })
                
                print(f"{'✅' if passed else '❌'} {test_case['test_name']}")
                for feature in features_found:
                    print(f"  {feature}")
                
            except Exception as e:
                results.append({
                    "test_name": test_case["test_name"],
                    "error": str(e),
                    "passed": False
                })
                print(f"❌ {test_case['test_name']}: Error - {e}")
        
        return results

    async def _test_edge_case_handling(self) -> List[Dict[str, Any]]:
        """
        Test edge case handling (20 points)
        """
        edge_cases = [
            {
                "test_name": "No charts available for visual user",
                "response": "## Analysis\n\nDetailed text analysis without any charts or graphs.",
                "user_input": "show me charts and graphs",
                "expected_fallback": True,
                "expected_message_type": "visual_fallback"
            },
            {
                "test_name": "Minimal text for text user",
                "response": "Brief note.",
                "user_input": "I want detailed explanations",
                "expected_fallback": True,
                "expected_message_type": "text_fallback"
            },
            {
                "test_name": "Low confidence preference",
                "response": "## Standard response\n\nNormal content here.",
                "user_input": "maybe some info",  # Ambiguous input
                "expected_fallback": True,
                "expected_message_type": "low_confidence"
            },
            {
                "test_name": "Empty response",
                "response": "",
                "user_input": "show me data",
                "expected_fallback": True,
                "expected_message_type": "empty_response"
            },
            {
                "test_name": "Very long response for visual user", 
                "response": "## Analysis\n\n" + "Very detailed analysis. " * 200,  # Long text
                "user_input": "show me visual charts",
                "expected_fallback": True,
                "expected_message_type": "truncation"
            }
        ]
        
        results = []
        
        for edge_case in edge_cases:
            try:
                formatted_result = await self.response_formatter.format_response_by_preference(
                    raw_response=edge_case["response"],
                    user_input=edge_case["user_input"]
                )
                
                fallback_applied = formatted_result["fallback_applied"]
                response_content = formatted_result["response"]
                
                # Check for appropriate fallback messages
                fallback_indicators = {
                    "visual_fallback": ["Visual Content Not Available", "charts and visual", "visual responses"],
                    "text_fallback": ["Additional Context", "detailed explanations", "comprehensive"],
                    "low_confidence": ["Personalized Response", "still learning", "preferences"],
                    "empty_response": ["Response Not Available", "not have sufficient", "try:"],
                    "truncation": ["optimized for visual preference", "Full details available"]
                }
                
                expected_indicators = fallback_indicators.get(edge_case["expected_message_type"], [])
                indicators_found = sum(1 for indicator in expected_indicators 
                                     if indicator.lower() in response_content.lower())
                
                passed = (
                    fallback_applied == edge_case["expected_fallback"] and
                    indicators_found > 0
                )
                
                results.append({
                    "test_name": edge_case["test_name"],
                    "user_input": edge_case["user_input"],
                    "expected_fallback": edge_case["expected_fallback"],
                    "actual_fallback": fallback_applied,
                    "expected_message_type": edge_case["expected_message_type"],
                    "indicators_found": indicators_found,
                    "indicators_expected": len(expected_indicators),
                    "passed": passed,
                    "confidence": formatted_result["confidence"],
                    "response_length": len(response_content)
                })
                
                print(f"{'✅' if passed else '❌'} {edge_case['test_name']}: Fallback {'applied' if fallback_applied else 'not applied'}")
                
                if fallback_applied:
                    self.test_stats["edge_cases_handled"] += 1
                
            except Exception as e:
                results.append({
                    "test_name": edge_case["test_name"],
                    "error": str(e),
                    "passed": False
                })
                print(f"❌ {edge_case['test_name']}: Error - {e}")
        
        return results

    async def _test_integration(self) -> List[Dict[str, Any]]:
        """
        Test end-to-end integration
        """
        # This would test the full pipeline from user input to formatted response
        integration_tests = [
            {
                "test_name": "Full pipeline - visual preference",
                "user_query": "Create charts showing market performance with visual data",
                "mock_agent_response": """
                ## Market Performance Analysis
                
                The market shows strong indicators across multiple sectors.
                
                ![Market Performance](public/market_perf.png)
                
                | Sector | Performance | Trend |
                |--------|-------------|-------|
                | Tech   | +15%        | ↑     |
                | Finance| +12%        | ↑     |
                
                Analysis indicates continued growth momentum.
                
                ![Sector Analysis](public/sectors.png)
                """,
                "expected_outcome": "visual_priority_formatting"
            }
        ]
        
        results = []
        
        for test in integration_tests:
            try:
                # Simulate full pipeline
                formatted_result = await self.response_formatter.format_response_by_preference(
                    raw_response=test["mock_agent_response"],
                    user_input=test["user_query"]
                )
                
                passed = (
                    formatted_result["formatting_applied"] in ["visual_priority", "text_priority", "balanced"] and
                    formatted_result["confidence"] > 0.5 and
                    len(formatted_result["response"]) > 0
                )
                
                results.append({
                    "test_name": test["test_name"],
                    "user_query": test["user_query"],
                    "expected_outcome": test["expected_outcome"],
                    "actual_formatting": formatted_result["formatting_applied"],
                    "confidence": formatted_result["confidence"],
                    "chart_count": formatted_result["metadata"]["chart_count"],
                    "text_sections": formatted_result["metadata"]["text_sections"],
                    "passed": passed
                })
                
                print(f"{'✅' if passed else '❌'} {test['test_name']}: {formatted_result['formatting_applied']}")
                
            except Exception as e:
                results.append({
                    "test_name": test["test_name"],
                    "error": str(e),
                    "passed": False
                })
                print(f"❌ {test['test_name']}: Error - {e}")
        
        return results

    async def _test_performance(self) -> List[Dict[str, Any]]:
        """
        Test system performance
        """
        # Performance benchmarks
        start_time = datetime.now()
        
        # Run multiple preference detections
        test_inputs = [
            "show me charts",
            "detailed analysis please", 
            "balanced information",
            "visual dashboard",
            "comprehensive explanations"
        ]
        
        detection_times = []
        
        for input_text in test_inputs:
            detection_start = datetime.now()
            await self.preference_detector.detect_preference(input_text)
            detection_end = datetime.now()
            detection_times.append((detection_end - detection_start).total_seconds())
        
        avg_detection_time = sum(detection_times) / len(detection_times)
        
        # Test response formatting performance
        test_response = "## Test\n\nSample response\n\n![Chart](public/test.png)\n\nMore content."
        
        format_start = datetime.now()
        await self.response_formatter.format_response_by_preference(
            raw_response=test_response,
            user_input="show me visual data"
        )
        format_end = datetime.now()
        
        format_time = (format_end - format_start).total_seconds()
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Performance criteria
        performance_passed = (
            avg_detection_time < 2.0 and  # Detection should be under 2 seconds
            format_time < 1.0 and         # Formatting should be under 1 second
            total_time < 10.0              # Total test time reasonable
        )
        
        return [{
            "test_name": "Performance benchmarks",
            "avg_detection_time": avg_detection_time,
            "format_time": format_time,
            "total_time": total_time,
            "detection_times": detection_times,
            "passed": performance_passed,
            "criteria": {
                "detection_under_2s": avg_detection_time < 2.0,
                "formatting_under_1s": format_time < 1.0,
                "total_under_10s": total_time < 10.0
            }
        }]

    async def _test_error_handling(self) -> List[Dict[str, Any]]:
        """
        Test error handling and graceful degradation
        """
        error_cases = [
            {
                "test_name": "Invalid JSON response",
                "response": "Invalid content {broken json",
                "user_input": "show data",
                "should_handle_gracefully": True
            },
            {
                "test_name": "Empty user input",
                "response": "Valid response content",
                "user_input": "",
                "should_handle_gracefully": True
            },
            {
                "test_name": "None inputs",
                "response": None,
                "user_input": None,
                "should_handle_gracefully": True
            }
        ]
        
        results = []
        
        for error_case in error_cases:
            try:
                if error_case["response"] is None or error_case["user_input"] is None:
                    # This should raise an exception
                    try:
                        await self.response_formatter.format_response_by_preference(
                            raw_response=error_case["response"],
                            user_input=error_case["user_input"]
                        )
                        # If we get here, the system didn't handle the error properly
                        passed = False
                    except Exception:
                        # Exception was raised as expected
                        passed = True
                else:
                    formatted_result = await self.response_formatter.format_response_by_preference(
                        raw_response=error_case["response"],
                        user_input=error_case["user_input"]
                    )
                    # System should return a valid response even with bad input
                    passed = (
                        "response" in formatted_result and
                        len(str(formatted_result["response"])) > 0
                    )
                
                results.append({
                    "test_name": error_case["test_name"],
                    "should_handle_gracefully": error_case["should_handle_gracefully"],
                    "passed": passed
                })
                
                print(f"{'✅' if passed else '❌'} {error_case['test_name']}")
                
            except Exception as e:
                # For None inputs, exceptions are expected
                if "None" in error_case["test_name"]:
                    passed = True
                else:
                    passed = False
                
                results.append({
                    "test_name": error_case["test_name"],
                    "error": str(e),
                    "passed": passed
                })
                
                print(f"{'✅' if passed else '❌'} {error_case['test_name']}: {e}")
        
        return results

    def _calculate_final_scores(self):
        """
        Calculate final scores based on test results
        """
        if self.test_stats["total_tests"] > 0:
            self.test_stats["preference_accuracy"] = (
                self.test_stats["passed_tests"] / self.test_stats["total_tests"]
            )
            self.test_stats["formatting_accuracy"] = (
                self.test_stats["passed_tests"] / self.test_stats["total_tests"] 
            )

    def _generate_final_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive final report
        """
        # Calculate scoring based on requirements
        preference_application_score = 0
        chart_text_balance_score = 0
        edge_case_handling_score = 0
        
        for category_result in self.test_results:
            category_name = category_result["category"]
            results = category_result["results"]
            passed_tests = sum(1 for r in results if r.get("passed", False))
            total_tests = len(results)
            success_rate = passed_tests / max(total_tests, 1)
            
            if "Response Ordering" in category_name:
                preference_application_score = min(20, int(success_rate * 20))
            elif "Chart/Text Balance" in category_name:
                chart_text_balance_score = min(20, int(success_rate * 20))
            elif "Edge Case Handling" in category_name:
                edge_case_handling_score = min(20, int(success_rate * 20))
        
        total_score = preference_application_score + chart_text_balance_score + edge_case_handling_score
        
        return {
            "test_suite_status": "completed",
            "timestamp": datetime.now().isoformat(),
            "system_availability": PREFERENCE_SYSTEM_AVAILABLE,
            
            # Scoring breakdown (60 points total)
            "scoring": {
                "preference_application": {
                    "score": preference_application_score,
                    "max_score": 20,
                    "description": "Apply Preference to Existing Responses"
                },
                "chart_text_balance": {
                    "score": chart_text_balance_score,
                    "max_score": 20,
                    "description": "Customize Chart/Text Balance"
                },
                "edge_case_handling": {
                    "score": edge_case_handling_score,
                    "max_score": 20,
                    "description": "Handle Edge Cases"
                },
                "total_score": total_score,
                "total_possible": 60,
                "percentage": (total_score / 60) * 100
            },
            
            # Test statistics
            "test_statistics": self.test_stats,
            
            # Detailed results by category
            "detailed_results": self.test_results,
            
            # Overall assessment
            "assessment": {
                "overall_success": total_score >= 48,  # 80% threshold
                "readiness_for_production": (
                    total_score >= 48 and 
                    self.test_stats["edge_cases_handled"] >= 3 and
                    PREFERENCE_SYSTEM_AVAILABLE
                ),
                "recommendations": self._generate_recommendations(total_score)
            },
            
            "success": True
        }

    def _generate_recommendations(self, total_score: int) -> List[str]:
        """
        Generate recommendations based on test results
        """
        recommendations = []
        
        if total_score < 48:
            recommendations.append("🔧 System needs improvement before production deployment")
        
        if not PREFERENCE_SYSTEM_AVAILABLE:
            recommendations.append("🚨 Preference system dependencies need to be installed")
        
        if self.test_stats["edge_cases_handled"] < 3:
            recommendations.append("⚠️ Edge case handling needs strengthening")
        
        if self.test_stats["failed_tests"] > 0:
            recommendations.append(f"🔍 {self.test_stats['failed_tests']} tests failed - review and fix")
        
        if total_score >= 48:
            recommendations.append("✅ System meets production readiness criteria")
            recommendations.append("🚀 Ready for deployment with comprehensive preference-based responses")
        
        return recommendations


# Main test runner
async def run_comprehensive_preference_tests():
    """
    Main function to run all preference system tests
    """
    test_suite = PreferenceSystemTestSuite()
    
    print("🧪 TheNZT Preference-Based Response System - Comprehensive Test Suite")
    print("📋 Testing 60-point scoring system implementation:")
    print("   • Apply Preference to Existing Responses (20 points)")
    print("   • Customize Chart/Text Balance (20 points)")
    print("   • Handle Edge Cases (20 points)")
    print("=" * 80)
    
    # Run all tests
    final_report = await test_suite.run_comprehensive_tests()
    
    # Display final results
    print("\n" + "=" * 80)
    print("🏆 FINAL TEST RESULTS")
    print("=" * 80)
    
    if final_report["success"]:
        scoring = final_report["scoring"]
        print(f"📊 PREFERENCE APPLICATION: {scoring['preference_application']['score']}/20 points")
        print(f"⚖️ CHART/TEXT BALANCE: {scoring['chart_text_balance']['score']}/20 points")
        print(f"🛡️ EDGE CASE HANDLING: {scoring['edge_case_handling']['score']}/20 points")
        print(f"🎯 TOTAL SCORE: {scoring['total_score']}/60 points ({scoring['percentage']:.1f}%)")
        
        print(f"\n📈 Test Statistics:")
        stats = final_report["test_statistics"]
        print(f"   • Total Tests: {stats['total_tests']}")
        print(f"   • Passed: {stats['passed_tests']}")
        print(f"   • Failed: {stats['failed_tests']}")
        print(f"   • Edge Cases Handled: {stats['edge_cases_handled']}")
        
        print(f"\n🔍 Assessment:")
        assessment = final_report["assessment"]
        print(f"   • Overall Success: {'✅' if assessment['overall_success'] else '❌'}")
        print(f"   • Production Ready: {'✅' if assessment['readiness_for_production'] else '❌'}")
        
        print(f"\n💡 Recommendations:")
        for rec in assessment["recommendations"]:
            print(f"   {rec}")
        
    else:
        print(f"❌ Test suite failed: {final_report.get('reason', 'Unknown error')}")
    
    return final_report


if __name__ == "__main__":
    asyncio.run(run_comprehensive_preference_tests())