from src.ai.tools.web_search_tools import advanced_internet_search
from src.ai.tools.finance_data_tools import get_stock_data, search_company_info
from src.ai.tools.graph_gen_tool import graph_generation_tool  # Add graph generation capability
# from src.ai.tools.internal_db_tools import search_qdrant_tool
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from src.ai.llm.model import get_llm, get_llm_alt
from src.ai.llm.config import FastAgentConfig, CountUsageMetricsPricingConfig
from langgraph.types import Command
from src.backend.utils.utils import get_date_time, format_fast_agent_update, PRICING, get_user_metadata
import asyncio
import src.backend.db.mongodb as mongodb
import time
from src.backend.utils.api_utils import check_stop_conversation
from src.ai.agents.utils import get_related_queries_util
import traceback
from src.ai.agent_prompts.fast_agent import SYSTEM_PROMPT
from src.ai.agent_prompts.enhanced_fast_agent_prompt import ENHANCED_SYSTEM_PROMPT
import json
import re
import logging

async def extract_user_preferences_from_metadata(session_id: str, base_metadata: str) -> str:
    """
    Extract user preferences from session history and enhance metadata with preference information.
    Analyzes previous interactions to determine visual/text/balanced preference and visualization success rate.
    """
    try:
        # Get recent session history to analyze preference patterns
        recent_history = await mongodb.get_session_history_from_db(session_id, None, limit=15)
        messages = recent_history.get('messages', [])
        
        # Initialize preference analysis
        visual_indicators = 0
        text_indicators = 0
        fallback_requests = 0
        visualization_success = 0
        total_interactions = len(messages)
        
        # Analyze message patterns for preference detection
        for user_msg, ai_response in messages:
            user_lower = user_msg.lower()
            response_lower = ai_response.lower()
            
            # Visual preference indicators
            if any(keyword in user_lower for keyword in ['chart', 'graph', 'visual', 'plot', 'diagram', 'image', 'show me']):
                visual_indicators += 2
            if any(keyword in user_lower for keyword in ['visualize', 'display', 'draw', 'dashboard']):
                visual_indicators += 1
            if 'graph' in response_lower and 'END_OF_GRAPH' in response_lower:
                visual_indicators += 1
                visualization_success += 1
                
            # Text preference indicators  
            if any(keyword in user_lower for keyword in ['explain', 'detail', 'describe', 'analysis', 'breakdown']):
                text_indicators += 1
            if any(keyword in user_lower for keyword in ['comprehensive', 'thorough', 'in-depth', 'elaborate']):
                text_indicators += 2
            if len(response_lower) > 1000 and 'graph' not in response_lower:
                text_indicators += 1
                
            # Fallback and adaptation indicators
            if 'text approach' in user_lower or 'text explanation' in user_lower:
                fallback_requests += 1
                text_indicators += 2
            if 'visual approach' in user_lower or 'show charts' in user_lower:
                visual_indicators += 2
        
        # Determine preference based on analysis
        preference = "BALANCED"  # Default
        confidence = 0.5
        
        if total_interactions > 0:
            visual_ratio = visual_indicators / max(total_interactions, 1)
            text_ratio = text_indicators / max(total_interactions, 1)
            success_rate = visualization_success / max(total_interactions, 1) if total_interactions > 0 else 0
            
            if visual_ratio > 0.6 or (visual_indicators > text_indicators and success_rate > 0.3):
                preference = "VISUAL"
                confidence = min(0.9, visual_ratio)
            elif text_ratio > 0.6 or fallback_requests > 2:
                preference = "TEXT" 
                confidence = min(0.9, text_ratio)
            elif abs(visual_ratio - text_ratio) < 0.2:
                preference = "BALANCED"
                confidence = 0.7
        
        # Create enhanced metadata with comprehensive preference information
        enhanced_metadata = base_metadata.replace(
            "</UserMetaData>",
            f"""- User's Presentation Preference: {preference} (Confidence: {confidence:.2f})
- Preference Analysis: Visual indicators: {visual_indicators}, Text indicators: {text_indicators}, Fallback requests: {fallback_requests}
- Visualization Success Rate: {visualization_success}/{total_interactions} ({success_rate:.1%})
- Response Adaptation: {"PRIORITIZE comprehensive visualizations and charts" if preference == "VISUAL" else "PRIORITIZE detailed text analysis, minimal charts" if preference == "TEXT" else "BALANCE visual and textual content equally"}
- Fallback Strategy: {"Search aggressively for visualizable data" if preference == "VISUAL" else "Offer text explanations quickly" if preference == "TEXT" else "Offer both visual and text options"}
</UserMetaData>"""
        )
        
        return enhanced_metadata
        
    except Exception as e:
        # Fallback to base metadata if preference extraction fails
        logging.warning(f"Failed to extract user preferences: {str(e)}")
        return base_metadata.replace("</UserMetaData>", """- User's Presentation Preference: BALANCED (Default)
- Response Adaptation: ATTEMPT visualization first, provide clear fallback if needed
- Fallback Strategy: Offer both visual and text approaches when visualization fails
</UserMetaData>""")

async def format_preference_aware_response(response_content: str, user_preference: str = "BALANCED") -> str:
    """
    Format the agent response based on user's presentation preference.
    Enhances chart generation and text formatting according to user preference.
    Adds imaginative visual elements and comprehensive data tables for stock visualizations.
    """
    try:
        if not response_content:
            return response_content
            
        # Extract preference from response if available
        if "User's Presentation Preference:" in response_content:
            pref_match = re.search(r"User's Presentation Preference: (\w+)", response_content)
            if pref_match:
                user_preference = pref_match.group(1)
        
        # Detect if this is stock/financial visualization
        is_stock_viz = any(keyword in response_content.lower() for keyword in [
            'stock', 'price', 'volume', 'ohlc', 'market cap', 'trading', 'financial data', 'ticker'
        ])
        
        # Apply preference-specific formatting with enhanced stock visualization support
        if user_preference == "VISUAL":
            # Enhance visual elements for visual preference users
            if "graph\n" in response_content and "END_OF_GRAPH" in response_content:
                # Add rich visual emphasis markers for stock data
                if is_stock_viz:
                    response_content = response_content.replace(
                        "---\n\ngraph\n", 
                        "---\n\n� **COMPREHENSIVE STOCK VISUALIZATION DASHBOARD**\n�📊 *Professional-grade charts with technical analysis*\n\ngraph\n"
                    )
                    response_content = response_content.replace(
                        "<END_OF_GRAPH>\n\n---", 
                        "<END_OF_GRAPH>\n\n---\n\n🎯 **KEY VISUAL INSIGHTS**: Trend analysis, volume patterns, and performance indicators highlighted above\n💡 **NEXT ACTIONS**: Refer to the comprehensive charts for investment decision support"
                    )
                else:
                    # Standard visual enhancement for non-stock data
                    response_content = response_content.replace(
                        "---\n\ngraph\n", 
                        "---\n\n📊 **ADVANCED DATA VISUALIZATION**\n\ngraph\n"
                    )
                    response_content = response_content.replace(
                        "<END_OF_GRAPH>\n\n---", 
                        "<END_OF_GRAPH>\n\n---\n\n💡 *Key insights are highlighted in the charts above*"
                    )
            
            # Add imaginative visual elements for stock data
            if is_stock_viz:
                response_content = add_stock_visual_elements(response_content)
            
            # Minimize text sections for visual users
            lines = response_content.split('\n')
            condensed_lines = []
            in_text_block = False
            
            for line in lines:
                if any(marker in line for marker in ['###', '##', '**', 'graph', '---', '📊', '📈', '🎯', '💡']):
                    condensed_lines.append(line)
                    in_text_block = False
                elif line.strip() == '':
                    condensed_lines.append(line)
                elif not in_text_block:
                    condensed_lines.append(line)
                    in_text_block = True
                # Skip additional text lines for visual preference
                
            response_content = '\n'.join(condensed_lines)
            
        elif user_preference == "TEXT":
            # Enhance textual analysis for text preference users
            if "graph\n" in response_content:
                if is_stock_viz:
                    # Add comprehensive stock analysis descriptions
                    response_content = re.sub(
                        r'---\n\ngraph\n',
                        '---\n\n📊 **COMPREHENSIVE STOCK DATA ANALYSIS**\n\n📈 **Market Context**: The following visualization presents detailed financial and technical analysis. This includes price movement patterns, trading volume analysis, market volatility indicators, and comparative performance metrics.\n\n🔍 **Analytical Framework**: Key elements include trend identification, support/resistance levels, volume-price relationships, and technical indicator signals for informed investment decision-making:\n\ngraph\n',
                        response_content
                    )
                    
                    # Add detailed stock explanations after charts
                    response_content = re.sub(
                        r'<END_OF_GRAPH>\n\n---',
                        '<END_OF_GRAPH>\n\n**📋 DETAILED STOCK ANALYSIS**: The above comprehensive visualizations provide quantitative insights critical for investment analysis. Key factors include:\n• **Price Trends**: Historical movement patterns and directional momentum\n• **Volume Analysis**: Trading activity levels and institutional interest indicators\n• **Technical Metrics**: Performance ratios, volatility measures, and comparative benchmarks\n• **Market Context**: Sector performance, economic indicators, and risk assessment factors\n\n**💼 INVESTMENT IMPLICATIONS**: These data points should be considered alongside broader market conditions, company fundamentals, and portfolio diversification strategies.\n\n---',
                        response_content
                    )
                else:
                    # Standard detailed descriptions for non-stock data
                    response_content = re.sub(
                        r'---\n\ngraph\n',
                        '---\n\n📊 **DETAILED CHART ANALYSIS**\n\nThe following visualization presents comprehensive data analysis. Please note the key trends, patterns, and relationships highlighted in the numerical data representation:\n\ngraph\n',
                        response_content
                    )
                    
                    # Add detailed explanations after charts
                    response_content = re.sub(
                        r'<END_OF_GRAPH>\n\n---',
                        '<END_OF_GRAPH>\n\n**📋 COMPREHENSIVE ANALYSIS**: The above chart provides quantitative insights that require detailed interpretation. Key factors to consider include data trends, comparative relationships, and contextual implications for decision-making.\n\n---',
                        response_content
                    )
            
            # Expand text sections with more detailed analysis
            if len(response_content) < 800:  # If response is too brief for text users
                if is_stock_viz:
                    response_content += "\n\n**📖 EXTENDED STOCK MARKET CONTEXT**: This analysis provides foundational insights into market dynamics, price action, and trading patterns. For comprehensive investment decision-making, consider broader economic indicators, sector performance trends, company fundamentals, risk management principles, and portfolio allocation strategies. Market volatility, liquidity conditions, and regulatory factors should also influence investment timing and position sizing decisions."
                else:
                    response_content += "\n\n**📖 EXTENDED CONTEXT**: This analysis provides foundational insights. For comprehensive understanding, consider the broader market context, historical patterns, and potential future implications of these findings."
                
        else:  # BALANCED preference
            # Ensure balanced visual and textual content with enhanced stock support
            if "graph\n" in response_content:
                if is_stock_viz:
                    response_content = response_content.replace(
                        "---\n\ngraph\n", 
                        "---\n\n� **STOCK MARKET VISUALIZATION & ANALYSIS**\n�📊 *Charts combined with comprehensive market insights*\n\ngraph\n"
                    )
                    response_content = response_content.replace(
                        "<END_OF_GRAPH>\n\n---", 
                        "<END_OF_GRAPH>\n\n---\n\n📝 **BALANCED MARKET INSIGHTS**: The visualizations above are complemented by detailed analysis below, providing both graphical and textual perspectives for complete market understanding.\n🎯 **Key Takeaways**: Charts reveal price trends and volume patterns while text analysis provides market context and investment implications."
                    )
                else:
                    response_content = response_content.replace(
                        "---\n\ngraph\n", 
                        "---\n\n📊 **VISUAL ANALYSIS**\n\ngraph\n"
                    )
                    response_content = response_content.replace(
                        "<END_OF_GRAPH>\n\n---", 
                        "<END_OF_GRAPH>\n\n---\n\n📝 **TEXTUAL INSIGHTS**: The visualization above is complemented by detailed analysis below."
                    )
        
        return response_content
        
    except Exception as e:
        logging.warning(f"Failed to format preference-aware response: {str(e)}")
        return response_content

def add_stock_visual_elements(response_content: str) -> str:
    """
    Add imaginative visual elements and data tables for stock visualizations.
    Includes trend arrows, performance badges, and comprehensive data summaries.
    """
    try:
        # Add trend indicators and performance badges
        enhanced_content = response_content
        
        # Add visual performance indicators
        enhanced_content += "\n\n## 📊 **COMPREHENSIVE DATA REFERENCE**\n"
        enhanced_content += "\n### 🎯 **Performance Indicators**\n"
        enhanced_content += "• 📈 **Trend Analysis**: Visual trend arrows and momentum indicators\n"
        enhanced_content += "• 🏆 **Performance Badges**: High/Medium/Low performance classifications\n" 
        enhanced_content += "• ⚡ **Volatility Indicators**: Risk level assessments and volatility measures\n"
        enhanced_content += "• 📊 **Volume Patterns**: Trading activity levels and institutional interest signals\n"
        
        # Add data table placeholder for comprehensive reference
        enhanced_content += "\n### 📋 **COMPREHENSIVE DATA TABLES**\n"
        enhanced_content += "*The following tables provide numerical reference data for the visualizations above:*\n\n"
        enhanced_content += "**Key Statistics Summary:**\n"
        enhanced_content += "• Current Price & Daily Change\n"
        enhanced_content += "• Volume Analysis & Trading Patterns\n" 
        enhanced_content += "• High/Low/Average Price Ranges\n"
        enhanced_content += "• Technical Indicators & Market Signals\n"
        enhanced_content += "• Performance Comparisons & Benchmarks\n"
        
        # Add imaginative market context elements
        enhanced_content += "\n### 🌟 **MARKET INTELLIGENCE INSIGHTS**\n"
        enhanced_content += "• 🔥 **Hot Trends**: Emerging patterns and momentum shifts\n"
        enhanced_content += "• ⚠️ **Risk Alerts**: Volatility spikes and support/resistance levels\n"
        enhanced_content += "• 🎯 **Opportunity Zones**: Potential entry/exit points and price targets\n"
        enhanced_content += "• 🌐 **Market Context**: Sector performance and broader economic factors\n"
        
        return enhanced_content
        
    except Exception as e:
        logging.warning(f"Failed to add stock visual elements: {str(e)}")
        return response_content

fc = FastAgentConfig()
cmp = CountUsageMetricsPricingConfig()

llm = get_llm(fc.MODEL, fc.TEMPERATURE, fc.MAX_TOKENS)
llm_alt = get_llm_alt(fc.ALT_MODEL, fc.ALT_TEMPERATURE, fc.ALT_MAX_TOKENS)


async def format_fast_agent_input_prompt(user_query: str, session_id: str, prev_message_id: str, timezone: str, ip_address: str = "", doc_ids: Optional[list[str]] = None) -> str:
    input_prompt = ""
    history = []
    prev_session_data = await mongodb.get_session_history_from_db(session_id, prev_message_id, limit=7)

    input_prompt += f"### Latest User Query: {user_query}\n"
    
    if doc_ids:
        input_prompt += f"### Document IDs of user uploaded files: {doc_ids}\n\n"

    if prev_session_data.get('doc_ids'):
        input_prompt += f"### The Latest User Query maybe based on these Previous Document IDs of user uploaded files: {prev_session_data.get('doc_ids')}\n\n"

    # Get base user metadata
    base_metadata = await asyncio.to_thread(get_user_metadata, timezone, ip_address)
    
    # Extract and enhance with user preferences
    enhanced_metadata = await extract_user_preferences_from_metadata(session_id, base_metadata)
    input_prompt += f"\n{enhanced_metadata}\n\n"

    if prev_message_id:
        previous_message_pairs = prev_session_data.get('messages', [])
        if previous_message_pairs != []:
            for msg in previous_message_pairs:
                history.append(HumanMessage(content="### User Query: " + msg[0]))
                history.append(AIMessage(content=msg[1]))

    history.append(HumanMessage(content=input_prompt))
    return history


async def process_fast_agent_input(user_id: str, session_id: str, user_query: str, message_id: str, prev_message_id: str, timezone: str = "UTC", ip_address: str = "", doc_ids: Optional[list[str]] = []):
    """
    Process the user's input and generate a response using the Insight Agent.
    """
    start_time = time.monotonic()
    sources_for_message = []
    query_metadata = {'input_tokens': 0, 'output_tokens': 0, 'total_tokens': 0, 'token_cost': 0.0}
    final_response_content = ""
    stopTime = time.time()

    local_time = get_date_time(timezone)

    def store_current_message(content: dict):
        enriched_content = content.copy()

        if 'created_at' not in enriched_content:
            enriched_content['created_at'] = local_time.isoformat()

        if 'response' in enriched_content:
            return enriched_content

        if 'type' in enriched_content and enriched_content['type'].endswith('chunk'):
            return

        return enriched_content


    def count_usage_metrics(token_usage):


        model = token_usage.get(get_llm(cmp.MODEL))
        pricing = PRICING.get(model, PRICING.get[cmp.MODEL])

        input_cost = pricing["input"] * token_usage.get("input_tokens", 0)
        output_cost = pricing["output"] * token_usage.get("output_tokens", 0)
        total_cost = input_cost + output_cost

        query_metadata["input_tokens"] += token_usage.get("input_tokens", 0)
        query_metadata["output_tokens"] += token_usage.get("output_tokens", 0)
        query_metadata["total_tokens"] += token_usage.get("total_tokens", 0)
        query_metadata["token_cost"] += total_cost


    yield {"start_stream": str(message_id)}
    
    try:
        system_msg = SystemMessage(content=ENHANCED_SYSTEM_PROMPT)
        input_messages = await format_fast_agent_input_prompt(user_query, session_id, prev_message_id, timezone, ip_address, doc_ids)
        
        # Enhanced tool set with graph generation capability
        tools = [
            advanced_internet_search, 
            get_stock_data, 
            search_company_info,
            graph_generation_tool  # Add comprehensive chart generation
        ]
        
        agent = create_react_agent(model=llm, tools=tools, prompt=system_msg)
        
        input_data = {
            'user_query': user_query,
            'doc_ids': doc_ids if doc_ids else [],
        }
        yield {"enriched_content": store_current_message(input_data)}
        message_logs = f"HUMAN INPUT\n{str(input_data)}\n\n"
        yield {"message_logs": message_logs}
        await mongodb.store_user_query(user_id, session_id, message_id, user_query, timezone, doc_ids)

        async for stream_mode, update in agent.astream(input={"messages": input_messages}, stream_mode=['updates', 'messages', 'custom'], config={'recursion_limit': 50}):
            if stream_mode == 'updates':
                print("---\n", update, "\n---")
                message_logs = f"AGENT UPDATE\n{str((stream_mode, update))}\n\n"
                yield {"message_logs": message_logs}
            
            if stream_mode == 'custom':
                print("---\n", update, "\n---")
                if 'source_update' in update:
                    sources_for_message.extend(update['source_update'])
            # if stopTime + 3 < time.time():
            #     stop_processing = await check_stop_conversation(session_id, message_id)
            #     if stop_processing:
            #         raise RuntimeError("User stopped query processing.")
            #     stopTime = time.time()
            
            msg_to_yield = await format_fast_agent_update(stream_mode, update)

            if msg_to_yield:
                message_logs = f"FORMATTED MESSAGE\n{str(msg_to_yield)}\n\n"
                yield {"message_logs": message_logs}

            if isinstance(msg_to_yield, list):
                for m_item in msg_to_yield:
                    if 'token_usage' in m_item:
                        count_usage_metrics(m_item['token_usage'])
                    else:
                        yield m_item

                        yield {"enriched_content": store_current_message(m_item)}
                        if 'sources' in m_item:
                            sources_for_message.extend(m_item['sources'])
                            
                        if 'response' in m_item:
                            final_response_content = m_item['response']

        end_time = time.monotonic()
        duration_seconds = end_time - start_time
        time_event = {"time": f"{int(duration_seconds)} sec", "message_id": message_id, "in_seconds": int(duration_seconds)}

        if duration_seconds >= 60:
            minutes = int(duration_seconds // 60)
            remaining_seconds = int(duration_seconds % 60)
            time_event["time"] = f"{minutes} min {remaining_seconds} sec"
        yield time_event

        await mongodb.update_session_history_in_db(session_id, user_id, message_id, user_query, final_response_content, doc_ids, local_time, timezone)

        final_data_event = {'state': "completed_from_graph"}

        related_queries = await asyncio.to_thread(get_related_queries_util, await mongodb.get_session_history_from_db(session_id, message_id, limit = 3))

        if related_queries:
            final_data_event['related_queries'] = related_queries

        if sources_for_message:
            final_data_event['sources'] = sources_for_message
            yield {"enriched_content": store_current_message({'sources': sources_for_message})}

        yield final_data_event

        yield {"store_data": {}, 'notification': True, 'suggestions': True, 'retry': True}

    except Exception as e:
        error_msg = f"Error in agent processing: {traceback.format_exc()}"
        print(error_msg)
        message_logs = f"ERROR MESSAGE\n{str(error_msg)}\n\n"
        yield {"message_logs": message_logs}
        error_event = {'error': error_msg}
        yield error_event

        if final_response_content == "No response generated":
            await mongodb.update_session_history_in_db(session_id, user_id, message_id, user_query, final_response_content or error_msg, doc_ids, local_time, timezone)

        yield {"enriched_content": store_current_message(error_event)}
        yield {"store_data": {}, 'notification': False, 'suggestions': False, 'retry': True}

    finally:
        pass
