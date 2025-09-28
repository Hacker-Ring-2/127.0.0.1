import requests
import json
import random
import time
from langchain_core.tools import tool, BaseTool
from typing import List, Literal, Type, Dict
import os 
from pydantic import BaseModel, Field
from src.ai.ai_schemas.tool_structured_input import GeocodeInput
from typing import Optional, List, Literal, Tuple, Dict
from src.ai.tools.graph_gen_tool_system_prompt import SYSTEM_PROMPT_STRUCT_OUTPUT
from dotenv import load_dotenv
from src.ai.llm.model import get_llm
from src.ai.llm.config import GraphGenerationConfig

# 🚀 IMPORT WORLD-CLASS VISUALIZER
from src.ai.tools.world_class_visualizer import world_class_visualizer
from src.ai.tools.smart_chart_generator import smart_chart_generator

load_dotenv()

ggc = GraphGenerationConfig()

# from smolagents import LiteLLMModel, CodeAgent

# def extract_markdown_tables_from_string(md_content):
#     """Extracts all markdown tables from a markdown string.

#     This function scans the provided markdown string and extracts any tables
#     written in GitHub Flavored Markdown format. A table is identified by a header
#     row containing '|' and a separator line immediately following it (with '-', ':' and '|').
#     The function returns each found table as a string (including header, separator, and rows).

#     Args:
#         md_content (str): The markdown content as a string.

#     Returns:
#         list of str: A list where each element is a string representation of a markdown table
#         found in the string, preserving line breaks within each table.
#     """
#     tables = []
#     current_table = []
#     in_table = False

#     # Split input string into lines
#     lines = md_content.splitlines()

#     for i, line in enumerate(lines):
#         line_strip = line.strip()

#         # Table header row: must contain '|' and not only dashes/spaces
#         if '|' in line_strip and not set(line_strip.replace('|', '').replace(' ', '')).issubset({'-', ':'}):
#             # Check next line for separator
#             if i + 1 < len(lines):
#                 next_line = lines[i + 1].strip()
#                 if (
#                     '|' in next_line
#                     and set(next_line.replace('|', '').replace(' ', '')).issubset({'-', ':'})
#                     and len(next_line.replace('|', '').replace(' ', '')) >= 3
#                 ):
#                     # Start of a new table
#                     in_table = True
#                     current_table.append(line.rstrip('\n'))
#                     continue

#         # If we're in a table, append lines
#         if in_table:
#             if line_strip == '' or not '|' in line_strip:
#                 # End of table
#                 if current_table:
#                     tables.append('\n'.join(current_table))
#                 current_table = []
#                 in_table = False
#             else:
#                 current_table.append(line.rstrip('\n'))

#     # Handle last table if string ends with a table
#     if current_table:
#         tables.append('\n'.join(current_table))

#     return tables

# Load the LLM
# AZURE_API_KEY = os.getenv("AZURE_API_KEY")
# AZURE_API_BASE = os.getenv("AZURE_API_BASE")

# llm = ChatLiteLLM(
#     model="azure/gpt-4.1-mini", 
#     temperature=0.1, 
#     azure_api_key=AZURE_API_KEY, 
#     api_base=AZURE_API_BASE
# )
# llm = ChatLiteLLM(
#     model="gemini/gemini-2.5-pro", 
#     temperature=0.1, 
#     # azure_api_key=AZURE_API_KEY, 
#     # api_base=AZURE_API_BASE
# )
llm = get_llm(model_name=ggc.MODEL, temperature=ggc.TEMPERATURE)

class SingleChartData(BaseModel):
    legend_label: str = Field(description="The legend label for the given data.")
    x_axis_data: List[str] = Field(description="List of values for the x-axis of the chart (will be converted to appropriate types during rendering)")
    y_axis_data: List[float] = Field(description="List of numerical values for the y-axis of the chart")
    color: str = Field(description="Color of the chart in Hex Color Code. Use only the color mentioned: `#1537ba`, `#00a9f4`, `#051c2c`, `#82a6c9`, `#99e6ff`, `#14b8ab`, `#9c217d`", max_length=7, min_length=7)


class StructOutput(BaseModel):
    chart_type: Literal['bar', 'group_bar', 'pie', 'lines'] = Field(description="Type of the chart to be generated")
    chart_title: str = Field(description="Title of the chart")
    x_label: str = Field(description="Label for the x-axis")
    y_label: str = Field(description="Label for the y-axis")    
    data: List[SingleChartData] = Field(description="List of ChartData, containing x and y axis data")
    

class StructOutputList(BaseModel):
    chart_collection: List[StructOutput] = Field(description="List of individual chart configurations to be generated from the input data. Each StructOutput represents one chart with its data and metadata. For STOCK/FINANCIAL data, generate 3-5 charts for comprehensive analysis. For NON-FINANCIAL data, generate exactly 1 chart.", min_length=1, max_length=5)


llm_struct_op = llm.with_structured_output(StructOutputList)


def generate_graphs_with_retry(md_content, max_retries=2):
    """
    Enhanced graph generation with retry logic and smart fallback strategies.
    Args:
        md_content: Raw table data in markdown format
        max_retries: Maximum number of retry attempts
    Returns:
        JSON string of chart configuration or "NO_CHART_GENERATED" if all attempts failed
    """
    print("🔄 GRAPH GENERATION WITH RETRY LOGIC")
    print(f"   Maximum retry attempts: {max_retries}")
    
    for attempt in range(max_retries + 1):
        print(f"\n🚀 Attempt {attempt + 1}/{max_retries + 1}")
        
        try:
            result = generate_graphs(md_content)
            
            if result != "NO_CHART_GENERATED":
                print(f"✅ SUCCESS on attempt {attempt + 1}")
                return result
            else:
                print(f"❌ Attempt {attempt + 1} failed: No charts generated")
                if attempt < max_retries:
                    print("   🔄 Retrying with modified approach...")
                    
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} crashed: {e}")
            if attempt < max_retries:
                print("   🔄 Retrying after error...")
    
    print(f"💀 All {max_retries + 1} API attempts failed")
    
    # SMART FALLBACK: Use API-free chart generation
    print("\n🧠 ACTIVATING SMART FALLBACK (API-FREE CHART GENERATION)")
    print("="*70)
    
    try:
        from src.ai.tools.smart_chart_generator import smart_chart_generator
        
        fallback_result = smart_chart_generator.generate_charts(md_content)
        
        if fallback_result != "NO_CHART_GENERATED":
            print("✅ SMART FALLBACK SUCCESSFUL! Charts generated without API dependency")
            return fallback_result
        else:
            print("❌ Smart fallback also failed")
            
    except Exception as fallback_error:
        print(f"❌ Smart fallback crashed: {fallback_error}")
        import traceback
        print("📝 Fallback error details:")
        print(traceback.format_exc())
    
    print("💀 All generation methods exhausted")
    return "NO_CHART_GENERATED"


def generate_graphs(md_content):
    """
    🚀 REVOLUTIONARY GRAPH GENERATION WITH WORLD-CLASS VISUALIZATION
    
    This function now uses our advanced world-class visualizer that creates
    stunning, interactive, professional charts with actual plotting!
    
    Args:
        md_content: Raw table data in markdown format
    Returns:
        JSON string of comprehensive chart analysis or fallback result
    """
    print("🚀" * 30)
    print("🎨 WORLD-CLASS FINANCIAL VISUALIZATION ENGINE")
    print("🚀" * 30)
    
    # First try our revolutionary world-class visualizer
    try:
        print("🎯 Attempting world-class visualization generation...")
        
        # Use the advanced visualizer that actually creates beautiful plots
        result = world_class_visualizer.generate_advanced_financial_charts(
            md_content, 
            theme='professional'  # Professional theme for financial data
        )
        
        if result['status'] == 'success' and result['chart_count'] > 0:
            print(f"✨ SUCCESS! Generated {result['chart_count']} world-class visualizations")
            print("📊 Chart types created:")
            for chart in result['charts']:
                print(f"   🎨 {chart['type']}: {chart['title']}")
            
            # Convert to the expected format for the frontend
            formatted_result = {
                "status": "success",
                "visualization_engine": "world_class",
                "chart_count": result['chart_count'],
                "charts": result['charts'],
                "insights": result['data_insights'],
                "generation_method": "advanced_plotly_visualization"
            }
            
            return json.dumps(formatted_result, ensure_ascii=False, indent=2)
        
        print("⚠️ World-class visualizer couldn't generate charts, trying fallback...")
        
    except Exception as e:
        print(f"❌ World-class visualizer error: {e}")
        print("🔄 Falling back to smart chart generator...")
    
    # Fallback to smart chart generator (API-free)
    try:
        print("🧠 Using smart chart generator as fallback...")
        smart_result = smart_chart_generator.generate_charts(md_content)
        
        if smart_result != "NO_CHART_GENERATED":
            print("✅ Smart chart generator succeeded!")
            return smart_result
        
        print("⚠️ Smart chart generator also failed, trying LLM approach...")
        
    except Exception as e:
        print(f"❌ Smart chart generator error: {e}")
    
    # Final fallback to original LLM-based approach
    return generate_graphs_llm_fallback(md_content)

def generate_graphs_llm_fallback(md_content):
    """
    Fallback LLM-based chart generation (original approach)
    """
    print("🔄 Using LLM fallback approach...")
    
    # Input validation and logging
    table = md_content
    print(f"📊 Input Data Analysis:")
    print(f"   - Raw input length: {len(table)} characters")
    print(f"   - Contains pipe characters (table indicators): {'|' in table}")
    print(f"   - Number of lines: {len(table.splitlines())}")
    print(f"   - First 200 chars: {table[:200]}...")
    
    # Enhanced input validation
    if not table or len(table.strip()) == 0:
        print("   ❌ Empty or whitespace-only input")
        return "NO_CHART_GENERATED"
    
    if '|' not in table:
        print("   ⚠️  No pipe characters detected - may not be valid markdown table")
    
    lines = table.splitlines()
    data_rows = [line for line in lines if '|' in line and not all(c in '|-: ' for c in line.replace('|', ''))]
    print(f"   - Estimated data rows: {len(data_rows)}")
    
    if len(data_rows) < 2:
        print("   ⚠️  Very few data rows detected - may be insufficient for chart generation")
    
    # Check for financial/stock data indicators
    financial_keywords = ['stock', 'price', 'volume', 'ohlc', 'open', 'high', 'low', 'close', 'market', 'trading', 'shares', 'ticker', 'exchange']
    is_financial_data = any(keyword.lower() in table.lower() for keyword in financial_keywords)
    print(f"   - Detected as financial/stock data: {is_financial_data}")
    
    if is_financial_data:
        print("   💰 FINANCIAL DATA DETECTED - Will attempt to generate 3-5 comprehensive charts")
    else:
        print("   📈 NON-FINANCIAL DATA - Will generate 1 optimized chart")

    # Construct LLM prompt with enhanced error recovery
    INPUT_PROMPT = f"""
The table is listed below:

{table}

IMPORTANT INSTRUCTIONS:
- Convert all x-axis values to strings (even numbers like years should be quoted as "2024")
- Ensure all y-axis values are numerical (floats)
- Use only colors from the approved palette: #1537ba, #00a9f4, #051c2c, #82a6c9, #99e6ff, #14b8ab, #9c217d
- Generate {'3-5 comprehensive charts' if is_financial_data else 'exactly 1 optimized chart'} for this data
- Provide clear, professional titles and labels
"""
    
    print(f"\n🤖 LLM Prompt Construction:")
    print(f"   - System prompt length: {len(SYSTEM_PROMPT_STRUCT_OUTPUT)} characters")
    print(f"   - Input prompt length: {len(INPUT_PROMPT)} characters")
    print(f"   - Total prompt length: {len(SYSTEM_PROMPT_STRUCT_OUTPUT + INPUT_PROMPT)} characters")
    print(f"   - Model being used: {ggc.MODEL} with temperature: {ggc.TEMPERATURE}")
    
    prompt = SYSTEM_PROMPT_STRUCT_OUTPUT + INPUT_PROMPT

    print(f"\n🚀 Invoking LLM for graph generation...")
    start_time = time.time()
    
    try:
        result = llm_struct_op.invoke(prompt)
        generation_time = time.time() - start_time
        print(f"   ✅ LLM invocation successful in {generation_time:.2f} seconds")
        
        struct_output = result
        print(f"\n📋 LLM Raw Output Analysis:")
        print(f"   - Output type: {type(struct_output)}")
        print(f"   - Output object: {struct_output}")
        
        dump = struct_output.model_dump()
        print(f"\n🔍 Structured Output Analysis:")
        print(f"   - Dump type: {type(dump)}")
        print(f"   - Contains chart_collection key: {'chart_collection' in dump}")
        
        if 'chart_collection' in dump:
            chart_collection = dump.get("chart_collection", [])
            print(f"   - Number of charts generated: {len(chart_collection)}")
            
            if len(chart_collection) == 0:
                print("   ❌ EMPTY CHART COLLECTION DETECTED")
                print("   📝 This indicates the LLM failed to generate any charts")
                print("   🔍 Possible causes: unclear data, prompt issues, or model limitations")
                return "NO_CHART_GENERATED"
            
            # Enhanced chart validation
            valid_charts = 0
            for idx, chart in enumerate(chart_collection):
                print(f"\n   📊 Chart {idx + 1} Validation:")
                print(f"      - Chart type: {chart.get('chart_type', 'MISSING')}")
                print(f"      - Title: {chart.get('chart_title', 'MISSING')}")
                
                # Validate required fields
                required_fields = ['chart_type', 'chart_title', 'x_label', 'y_label', 'data']
                missing_fields = [field for field in required_fields if not chart.get(field)]
                
                if missing_fields:
                    print(f"      ❌ Missing required fields: {missing_fields}")
                    continue
                
                # Validate chart data
                chart_data = chart.get('data', [])
                if not chart_data:
                    print(f"      ❌ Chart {idx + 1} has no data series")
                    continue
                
                valid_series = 0
                for data_idx, data_series in enumerate(chart_data):
                    x_data = data_series.get('x_axis_data', [])
                    y_data = data_series.get('y_axis_data', [])
                    color = data_series.get('color', '')
                    legend = data_series.get('legend_label', '')
                    
                    print(f"         - Series {data_idx + 1}: {len(x_data)} x-points, {len(y_data)} y-points")
                    print(f"         - Legend: {legend}")
                    print(f"         - Color: {color}")
                    
                    # Validate data series
                    if not x_data or not y_data:
                        print(f"         ❌ Empty x or y data in series {data_idx + 1}")
                        continue
                    
                    if len(x_data) != len(y_data):
                        print(f"         ❌ Mismatched x/y data lengths: {len(x_data)} vs {len(y_data)}")
                        continue
                    
                    if not color.startswith('#') or len(color) != 7:
                        print(f"         ⚠️  Invalid color format: {color}")
                    
                    valid_series += 1
                
                if valid_series > 0:
                    print(f"      ✅ Chart {idx + 1} is valid with {valid_series} data series")
                    valid_charts += 1
                else:
                    print(f"      ❌ Chart {idx + 1} has no valid data series")
            
            if valid_charts == 0:
                print("   ❌ NO VALID CHARTS FOUND")
                return "NO_CHART_GENERATED"
            
            print(f"   ✅ {valid_charts} out of {len(chart_collection)} charts are valid")
                    
        else:
            print("   ❌ NO chart_collection KEY FOUND IN OUTPUT")
            return "NO_CHART_GENERATED"

        # Success validation and final JSON generation
        json_output = json.dumps(dump, ensure_ascii=False)
        print(f"\n✅ GRAPH GENERATION SUCCESSFUL")
        print(f"   - Final JSON length: {len(json_output)} characters")
        print(f"   - Valid charts generated: {valid_charts}")
        print(f"   - Total generation time: {generation_time:.2f} seconds")
        print("="*80)
        
        return json_output
        
    except Exception as e:
        generation_time = time.time() - start_time
        print(f"   ❌ LLM invocation failed after {generation_time:.2f} seconds")
        print(f"   📝 Error details: {str(e)}")
        print(f"   🔍 Error type: {type(e).__name__}")
        
        # Enhanced error analysis with specific recovery suggestions
        error_str = str(e).lower()
        if "timeout" in error_str:
            print("   🕐 TIMEOUT ERROR - Consider reducing prompt size or using faster model")
        elif "token" in error_str or "limit" in error_str:
            print("   🔤 TOKEN LIMIT ERROR - Prompt or output too large")
        elif "rate" in error_str:
            print("   🚦 RATE LIMIT ERROR - Too many requests, consider implementing delays")
        elif "503" in error_str or "unavailable" in error_str:
            print("   🔌 SERVICE UNAVAILABLE - API service is down, consider fallback model")
        elif "union" in error_str or "type" in error_str:
            print("   � TYPE ERROR - Pydantic model compatibility issue")
        elif "api" in error_str or "connection" in error_str:
            print("   🌐 CONNECTION ERROR - Check API keys and network connectivity")
        else:
            print("   🔧 UNKNOWN ERROR - May require prompt adjustment or model change")
        
        # Log full error for debugging
        print(f"   🐛 Full error trace available for debugging: {e}")
        
        print("="*80)
        return "NO_CHART_GENERATED"

    # # tables = extract_markdown_tables_from_string(md_content)
    # # results = []

    # if not tables:
    #     print("No tables")
    #     return "NO_CHART_GENERATED"
    
    # for idx, table in enumerate(tables, start=1):        
    #     INPUT_PROMPT = f"""
    #     The table is listed below:

    #     \n{table}\n

    #     """
    #     print(f"INPUT_PROMPT = {INPUT_PROMPT}")
    #     prompt = SYSTEM_PROMPT_STRUCT_OUTPUT + INPUT_PROMPT

    #     try:
    #         result = llm_struct_op.invoke(prompt)
    #         struct_output = result
    #         print(f"Output from graph generator struct_output= {struct_output}")
    #         dump = struct_output.model_dump()
    #         print(f"Output from graph generator dump= {dump}")

    #         # if the LLM returns an empty chart_collection, treat that as a failure
    #         if not dump.get("chart_collection"):
    #             print(f"[Table {idx}] no charts in output.")
    #             return "NO_CHART_GENERATED"
            
    #         results.append(dump)
    #         # print(f"struct_output.model_dump() = {struct_output.model_dump()}")
    #     except Exception as e:
    #         print(f"[Table {idx}] Could not generate graphs: {e}")
    #         return "NO_CHART_GENERATED"
    #     # results.append(struct_output.model_dump())
    #     # print(f"[Table {y}] JS Code:\n{struct_output}\n{'-'*30}")

    

    # return json.dumps(results, ensure_ascii=False)


class GraphGenToolInput(BaseModel):
    table: str = Field(description="Provide a table containing numerical data of similar property in markdown format to create the visualization chart.")


class GraphGenTool(BaseTool):
    name: str = "graph_generation_tool"
    description: str = """
    Use this tool to generate a visualization chart by providing the table in markdown format. The tool returns formatted data in json format.
    """
    args_schema: Type[BaseModel] = GraphGenToolInput

    def _run(self, table: str) -> str:
        print(f"---TOOL CALL: graph_generation_tool \n --- \n Table: \n{table}\n --- \n")
        # Use retry logic for enhanced reliability
        output_string = generate_graphs_with_retry(table)

        if output_string == "NO_CHART_GENERATED":
            return "No chart generated; please skip creating any ```graph``` block for this table in the response."
        
        print(f"return from generate_graphs_with_retry = {output_string}")

        return output_string

graph_generation_tool = GraphGenTool()
graph_tool_list = [graph_generation_tool]



# def generate_graphs(md_content):
#     tables = extract_markdown_tables_from_string(md_content)
    
#     # output_dir = "output_graphs/"
#     # os.makedirs(output_dir, exist_ok=True)

#     results = []

    
#     for y, table in enumerate(tables, start=1):
        
#         INPUT_PROMPT = f"""
#         The table is listed below:

#         \n{table}\n

#         """

#         # result = agent.run(SYSTEM_PROMPT + INPUT_PROMPT)

#         # if "```python" not in result:
#         #     results.append(result)
#         # else:
#         #     results.append("NO GRAPH GENERATED!.")

#         prompt = SYSTEM_PROMPT_STRUCT_OUTPUT + INPUT_PROMPT
#         try:
#             result = llm_struct_op.invoke(prompt)
#             struct_output = result
#             print(f"struct_output.model_dump() = {struct_output.model_dump()}")
#         except Exception as e:
#             print(f"Could not generate graphs: {e}")

#         results.append(struct_output.model_dump())
#         print(f"[Table {y}] JS Code:\n{struct_output}\n{'-'*30}")

#     return json.dumps(results, ensure_ascii=False)

