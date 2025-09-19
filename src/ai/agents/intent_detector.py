from .base_agent import BaseAgent
from src.ai.ai_schemas.structured_responses import IntentDetection
from src.ai.agent_prompts.intent_detector import SYSTEM_PROMPT
from typing import Dict, Any, Literal
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.types import Command
from langgraph.graph import END
import json
from src.ai.llm.model import get_llm, get_llm_alt
from src.ai.llm.config import IntentDetectionConfig

cfg = IntentDetectionConfig()


class IntentDetector(BaseAgent):
    def __init__(self):
        super().__init__()
        self.model = get_llm(cfg.MODEL, cfg.TEMPERATURE)
        self.model_alt = get_llm_alt(cfg.ALT_MODEL, cfg.ALT_TEMPERATURE)
        self.response_schema = IntentDetection
        self.system_prompt = SYSTEM_PROMPT

    def format_input_prompt(self, state: Dict[str, Any]) -> str:
        input_prompt = ""
        history = []

        input_prompt += f"### Latest User Query: {state['user_query']}\n"
        if state.get('doc_ids'):
            input_prompt += f"### Document IDs of user uploaded files: {state['doc_ids']}\n\n"
        if state.get('prev_doc_ids'):
            input_prompt += f"### The Latest User Query maybe based on these Previous Document IDs of user uploaded files: {state['prev_doc_ids']}\n\n"
        if state.get('file_path'):
            input_prompt += f"### File Path: {state['file_path']}\n"

        if state.get('file_content'):
            input_prompt += f"### File Content: {state['file_content']}\n"

        input_prompt += f"\n{state['user_metadata']}\n\n"

        if state.get('previous_messages'):
            for msg in state['previous_messages'] :
                history.append(HumanMessage(content="### User Query: " + msg[0]))
                history.append(AIMessage(content=msg[1]))

        # input_prompt += f"### {state['currency_rates']}\n"
        print("Input prompt :", __name__, " : ", input_prompt)
        history.append(HumanMessage(content=input_prompt))
        return history

    def __call__(self, state: Dict[str, Any]) -> Command[Literal["Manager Agent", "Planner Agent", "DB Search Agent", "__end__"]]:
        history = self.format_input_prompt(state)
        messages = [SystemMessage(content=self.system_prompt)] + history

        try:
            output = self.model.invoke(input=messages, response_format=self.response_schema)
            # print("From Inside Intent Detector")
            # print(f"input to llm = \n{messages}\n")
            # print(f"output of llm = \n{output}\n")
        except Exception as e:
            print(f"Falling back to alternate model: {str(e)}")
            try:
                output = self.model_alt.invoke(input=messages, response_format=self.response_schema)
            except Exception as e:
                print(f"Error occurred in fallback model: {str(e)}")
                raise e

        response = json.loads(output.content)
        print(f"response from llm (json.loads(output.content)) = \n{response}\n")

        if not response.get('reject_query', False):
            if not response.get('response_to_user'):
                
                # Compute fixed progress
                current_progress = state.get("progress_bar", 0.0)
                progress = min(current_progress + 10.0, 100.0)
        
                print(f"===Progress in Intent Detector Agent: {progress}===")
                
                if not state.get('realtime_info') and (response.get('query_intent') and any(intent in response.get('query_intent') for intent in ('historical', 'factual'))):
                    return Command(
                        goto="DB Search Agent",
                        update={
                            "messages": output,
                            "query_tag": response.get('query_tag'),
                            "is_relevant_query": True,
                            "progress": progress
                        }
                    )
                    
                else:
                    if state['reasoning']:
                        agent_name = "Manager Agent"
                    else:
                        agent_name = "Planner Agent"
                        
                    return Command(
                        goto=agent_name,
                        update={
                            "messages": output,
                            "query_tag": response.get('query_tag'),
                            "formatted_user_query": response.get('formatted_user_query'),
                            "is_relevant_query": True,
                            "progress_bar": progress
                        }
                    )

            else:
                return Command(
                    goto=END,
                    update={
                        "messages": output,
                        "is_relevant_query": True,
                        "final_response": response.get("response_to_user", "No response provided."),
                        "progress_bar": 10.0  # still show some progress before ending
                    }
                )
        else:
            return Command(
                goto=END,
                update={
                    "messages": output,
                    "is_relevant_query": False,
                    "final_response": response.get("response_to_user", "Please provide more information."),
                    "progress_bar": 0.0  # no progress if query is rejected
                }
            )
