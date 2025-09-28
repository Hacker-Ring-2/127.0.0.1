import sys
import os
sys.path.append('.')

# Test imports to validate the implementation
try:
    from src.ai.agent_prompts.enhanced_fast_agent_prompt import ENHANCED_SYSTEM_PROMPT
    print('✅ Enhanced System Prompt imported successfully')
    print(f'   Prompt length: {len(ENHANCED_SYSTEM_PROMPT)} characters')
    
    # Check key sections
    key_sections = [
        'User_Preference_Integration',
        'VISUAL Preference Handling',
        'TEXT Preference Handling', 
        'BALANCED Preference Handling',
        'Advanced_Chart_Generation_Rules'
    ]
    
    for section in key_sections:
        if section in ENHANCED_SYSTEM_PROMPT:
            print(f'   ✅ {section}: Found')
        else:
            print(f'   ❌ {section}: Missing')
            
except ImportError as e:
    print(f'❌ Import failed: {e}')

try:
    from src.ai.agents.fast_agent import extract_user_preferences_from_metadata, format_preference_aware_response
    print('✅ Enhanced Fast Agent functions imported successfully')
except ImportError as e:
    print(f'❌ Fast Agent import failed: {e}')
    
print('🎯 Implementation validation complete')