import json
from typing import Any
from langchain.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
import logging
import re

logger = logging.getLogger(__name__)
llm = ChatOllama(model="llama3.1:8b", temperature=0)


def sanitize_llm_json(raw: str) -> Any:
    """
    Attempts to convert LLM-generated 'almost JSON' into valid JSON.

    Fixes:
    - Invalid \' escapes
    - Unescaped double quotes inside strings
    - Trailing commas
    """

    if not raw or not raw.strip():
        raise Exception("Empty input")

    text = raw.strip()

    # 1. Remove invalid escaped single quotes: \' → '
    text = re.sub(r"\\'", "'", text)

    # 2. Remove trailing commas before ] or }
    text = re.sub(r",\s*([\]}])", r"\1", text)

    # 3. Ensure wrapped in array if it looks like objects only
    if text.startswith("{") and text.endswith("}"):
        text = f"[{text}]"

    # 4. Validate JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise Exception(
            f"Failed to sanitize JSON.\n" f"Error: {e}\n" f"Sanitized text:\n{text}"
        ) from e


def analyze_with_llm(snapshot_path: str, selector: str):
    """
    Calls LLM and returns structured decision.
    """
    with open(snapshot_path, "r", encoding="utf-8") as f:
        text = f.read()

    LLM_SYSTEM_PROMPT = f"""
    You are a Playwright automation expert in python language.

    Analyze the Snapshot and the Selector.
    Return a ranked JSON list of Playwright locators alongwith confidence and reason 
    for the locators that may be probable match for the Original selector. The locator should
    be playwright locator in python language eg: page.get_by_role('button',name='abc') 
    which are generated using the rules as mentioned below.
    Return the output ONLY in the Return format below as a valid json string without
    any comments.  

    Snapshot:
    {text}

    Original Selector:
    {selector}

    Rules:
    You MUST return STRICT JSON that:
    - Uses double quotes for all keys and string values
    - Never uses single-quote escaping (\')
    - Only uses valid JSON escape sequences: \", \\ , \n, \t, \r
    - Can be parsed using Python json.loads() without errors
    - ALWAYS uses single quotes (') inside the locator and for attribute names
      eg: page.locator('//button[@type='submit']'). The value field in the return response 
      should be expression inside page.locator.
    - For xpath and css locators uses page.locator('...').
    - Prioritizes role based locators over others.
    - ONLY following locators are supported. You should return only one of these:
        page.get_by_alt_text
        page.get_by_label
        page.get_by_placeholder
        page.get_by_role
        page.get_by_test_id
        page.get_by_text
        page.get_by_title
        page.locator

    Return:
    [
    {{
        "locator": "...",
        "value": "....",
        "role": "....",
        "attributes": "....",
        "confidence": 0.0-1.0,
        "strategy": "role|testid|text|attribute|xpath",
        "reason": "..."
    }}
    ]
    """

    prompt = {
        "snapshot": text,
        "language": "python",
        "tool": "playwright",
        "original_selector": selector,
    }

    llm_response_text = call_llm(system=LLM_SYSTEM_PROMPT, user=json.dumps(prompt))
    logger.info(f"LLM Response: {llm_response_text}")
    try:
        decision = sanitize_llm_json(llm_response_text)
    except json.JSONDecodeError as e:
        logger.error(e.msg)
        logger.error(f"Line:  {e.lineno}, Column:, {e.colno}")
        return {
            "action": "FLAG_FOR_REVIEW",
            "details": {},
            "reasoning": "LLM returned invalid JSON",
        }

    return decision


def call_llm(system: str, user: str) -> str:
    sys_msg = SystemMessage(system)
    user_msg = HumanMessage(user)
    messages = [sys_msg, user_msg]
    response = llm.invoke(messages)
    return response.content
