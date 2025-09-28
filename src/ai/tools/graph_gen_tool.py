import requests
import json
import random
import time
from langchain_core.tools import tool, BaseTool
from typing import List, Literal, Type, Dict
import os 
from pydantic import BaseModel, Field
from src.ai.ai_schemas.tool_structured_input import GeocodeInput
from typing import Optional, List, Literal, Tuple, Dict, Union
from src.ai.tools.graph_gen_tool_system_prompt import SYSTEM_PROMPT_STRUCT_OUTPUT
# from langchain_litellm import ChatLiteLLM
# from langchain_community.chat_models import ChatLiteLLM
from dotenv import load_dotenv
from src.ai.llm.model import get_llm
from src.ai.llm.config import GraphGenerationConfig

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
    x_axis_data: List[Union[float, str]] = Field(description="List of values for the x-axis of the chart")
    y_axis_data: List[float] = Field(description="List of values for the y-axis of the chart")
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


def generate_graphs(md_content):
    """
    Enhanced graph generation function with comprehensive debugging.
    Args:
        md_content: Raw table data in markdown format
    Returns:
        JSON string of chart configuration or "NO_CHART_GENERATED" if failed
    """
    print("="*80)
    print("🔍 GRAPH GENERATION DEBUG SESSION STARTING")
    print("="*80)
    
    # Input validation and logging
    table = md_content
    print(f"📊 Input Data Analysis:")
    print(f"   - Raw input length: {len(table)} characters")
    print(f"   - Contains pipe characters (table indicators): {'|' in table}")
    print(f"   - Number of lines: {len(table.splitlines())}")
    print(f"   - First 200 chars: {table[:200]}...")
    
    # Check for financial/stock data indicators
    financial_keywords = ['stock', 'price', 'volume', 'ohlc', 'open', 'high', 'low', 'close', 'market', 'trading', 'shares']
    is_financial_data = any(keyword.lower() in table.lower() for keyword in financial_keywords)
    print(f"   - Detected as financial/stock data: {is_financial_data}")
    
    if is_financial_data:
        print("   💰 FINANCIAL DATA DETECTED - Will attempt to generate 3-5 comprehensive charts")
    else:
        print("   📈 NON-FINANCIAL DATA - Will generate 1 optimized chart")

    # Construct LLM prompt
    INPUT_PROMPT = f"""
The table is listed below:

\n{table}\n

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
            
            # Analyze each chart
            for idx, chart in enumerate(chart_collection):
                print(f"\n   📊 Chart {idx + 1} Analysis:")
                print(f"      - Chart type: {chart.get('chart_type', 'MISSING')}")
                print(f"      - Title: {chart.get('chart_title', 'MISSING')}")
                print(f"      - Data series count: {len(chart.get('data', []))}")
                
                # Validate chart data
                chart_data = chart.get('data', [])
                if not chart_data:
                    print(f"      ❌ Chart {idx + 1} has no data series")
                else:
                    for data_idx, data_series in enumerate(chart_data):
                        x_data = data_series.get('x_axis_data', [])
                        y_data = data_series.get('y_axis_data', [])
                        print(f"         - Series {data_idx + 1}: {len(x_data)} x-points, {len(y_data)} y-points")
                        print(f"         - Legend: {data_series.get('legend_label', 'MISSING')}")
                        print(f"         - Color: {data_series.get('color', 'MISSING')}")
        else:
            print("   ❌ NO chart_collection KEY FOUND IN OUTPUT")
            return "NO_CHART_GENERATED"

        # Success validation
        json_output = json.dumps(dump, ensure_ascii=False)
        print(f"\n✅ GRAPH GENERATION SUCCESSFUL")
        print(f"   - Final JSON length: {len(json_output)} characters")
        print(f"   - Charts generated: {len(chart_collection)}")
        print(f"   - Total generation time: {generation_time:.2f} seconds")
        print("="*80)
        
        return json_output
        
    except Exception as e:
        generation_time = time.time() - start_time
        print(f"   ❌ LLM invocation failed after {generation_time:.2f} seconds")
        print(f"   📝 Error details: {str(e)}")
        print(f"   🔍 Error type: {type(e).__name__}")
        
        # Enhanced error analysis
        if "timeout" in str(e).lower():
            print("   🕐 TIMEOUT ERROR - Consider reducing prompt size or using faster model")
        elif "token" in str(e).lower():
            print("   🔤 TOKEN LIMIT ERROR - Prompt or output too large")
        elif "rate" in str(e).lower():
            print("   🚦 RATE LIMIT ERROR - Too many requests")
        elif "api" in str(e).lower():
            print("   🔌 API CONNECTION ERROR - Check API keys and connectivity")
        else:
            print("   🔧 UNKNOWN ERROR - May require prompt adjustment or model change")
        
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
        output_string = generate_graphs(table)

        if output_string == "NO_CHART_GENERATED":
            return "No chart generated; please skip creating any ```graph``` block for this table in the response."
        
        print(f"return from generate_graphs = {output_string}")

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

