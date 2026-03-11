# import json
# from typing import AsyncGenerator

# from mcp import ClientSession
# from mcp.client.sse import sse_client

# from prompts.system_prompt import build_system_prompt
# from utils.config import settings
# from utils.logger import get_logger

# logger = get_logger("agent")


# # ══════════════════════════════════════════════════════════════════════════════
# # LLM CLIENT
# # ══════════════════════════════════════════════════════════════════════════════
# def get_llm_client():
#     provider = settings.llm_provider
#     if provider == "groq":
#         from groq import Groq
#         logger.info("[Agent] Using Groq LLM")
#         return Groq(api_key=settings.groq_api_key)
#     elif provider == "ollama":
#         from openai import OpenAI
#         logger.info("[Agent] Using Ollama LLM")
#         return OpenAI(base_url=f"{settings.ollama_base_url}/v1", api_key="ollama")
#     elif provider == "openai":
#         from openai import OpenAI
#         logger.info("[Agent] Using OpenAI LLM")
#         return OpenAI(api_key=settings.openai_api_key)
#     else:
#         raise ValueError(f"Unsupported LLM_PROVIDER: '{provider}'. Use groq | ollama | openai")


# def get_model_name() -> str:
#     provider = settings.llm_provider
#     if provider == "groq":   return settings.groq_model
#     if provider == "ollama": return settings.ollama_model
#     if provider == "openai": return settings.openai_model
#     return "unknown"


# # ── MCP Server SSE URL ─────────────────────────────────────────────────────────
# MCP_SERVER_URL = "http://localhost:8001/sse"

# # ── Tool Schemas (access_token NEVER included — injected in Python) ───────────
# TOOL_SCHEMAS = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_employee_record",
#             "description": (
#                 "Fetch the Zoho People profile of the logged-in employee. "
#                 "Returns employee_zoho_id (numeric), designation, department, manager, etc. "
#                 "Call this FIRST before any leave operation to get employee_zoho_id."
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "employee_email": {
#                         "type": "string",
#                         "description": "Work email e.g. anjali.mahapatra@prodevans.com",
#                     },
#                 },
#                 "required": ["employee_email"],
#             },
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_leave_balance",
#             "description": (
#                 "Fetch leave balance for all leave types. "
#                 "Returns leave_type_id (numeric string), leave_type_name, days_available. "
#                 "MUST call this before apply_leave to get the correct numeric leave_type_id."
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "employee_zoho_id": {
#                         "type": "string",
#                         "description": "Numeric Zoho ID from get_employee_record e.g. 46224000012838001",
#                     },
#                 },
#                 "required": ["employee_zoho_id"],
#             },
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_leave_records",
#             "description": (
#                 "Fetch recent leave history of an employee. "
#                 "Returns leave_record_id needed for cancellation."
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "employee_zoho_id": {
#                         "type": "string",
#                         "description": "Numeric Zoho ID from get_employee_record.",
#                     },
#                     "number_of_records": {
#                         "type": "integer",
#                         "description": "Number of records to fetch. Default 5.",
#                     },
#                 },
#                 "required": ["employee_zoho_id"],
#             },
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "apply_leave",
#             "description": (
#                 "Submit a leave application. "
#                 "REQUIRED STEPS before calling: "
#                 "1) call get_employee_record to get employee_zoho_id. "
#                 "2) call get_leave_balance to get numeric leave_type_id. "
#                 "3) confirm dates and reason with employee. "
#                 "leave_type_id MUST be a numeric string like 46224000000210011, NOT a name."
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "employee_zoho_id": {
#                         "type": "string",
#                         "description": "Numeric Zoho ID from get_employee_record.",
#                     },
#                     "leave_type_id": {
#                         "type": "string",
#                         "description": "Numeric leave type ID from get_leave_balance. e.g. 46224000000210011. NOT a name.",
#                     },
#                     "leave_from_date": {
#                         "type": "string",
#                         "description": "Start date in DD-MMM-YYYY format e.g. 15-Mar-2026.",
#                     },
#                     "leave_to_date": {
#                         "type": "string",
#                         "description": "End date in DD-MMM-YYYY format e.g. 16-Mar-2026.",
#                     },
#                     "leave_reason": {
#                         "type": "string",
#                         "description": "Reason for leave e.g. fever.",
#                     },
#                 },
#                 "required": ["employee_zoho_id", "leave_type_id", "leave_from_date", "leave_to_date", "leave_reason"],
#             },
#         },
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "cancel_leave",
#             "description": (
#                 "Cancel an existing leave application. "
#                 "Call get_leave_records first to get leave_record_id if not known."
#             ),
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "leave_record_id": {
#                         "type": "string",
#                         "description": "Leave record ID from get_leave_records.",
#                     },
#                     "cancellation_reason": {
#                         "type": "string",
#                         "description": "Reason for cancellation.",
#                     },
#                 },
#                 "required": ["leave_record_id"],
#             },
#         },
#     },
# ]


# def _call_llm(llm_client, model_name: str, messages: list, use_tools: bool = True):
#     """
#     Calls LLM with or without tools.
#     Handles Groq tool_use_failed by retrying without tools.
#     """
#     try:
#         kwargs = dict(
#             model       = model_name,
#             messages    = messages,
#             max_tokens  = 4096,
#             temperature = 0.1,
#             stream      = False,
#         )
#         if use_tools:
#             kwargs["tools"]               = TOOL_SCHEMAS
#             kwargs["tool_choice"]         = "auto"
#             kwargs["parallel_tool_calls"] = False

#         return llm_client.chat.completions.create(**kwargs)

#     except Exception as e:
#         err_str = str(e)
#         # Groq tool_use_failed — model generated bad tool XML, retry without tools
#         if "tool_use_failed" in err_str or ("400" in err_str and "tool" in err_str.lower()):
#             logger.warning(f"[Agent] tool_use_failed — retrying without tools")
#             return llm_client.chat.completions.create(
#                 model       = model_name,
#                 messages    = messages,
#                 max_tokens  = 1024,
#                 temperature = 0.1,
#                 stream      = False,
#             )
#         # Rate limit — re-raise with clear message
#         if "429" in err_str or "rate_limit" in err_str.lower():
#             raise RuntimeError(f"Groq rate limit reached. Please wait a few minutes and try again.") from e
#         raise


# async def stream_chat(
#     conversation_messages: list,
#     employee_info:         dict,
#     access_token:          str,
# ) -> AsyncGenerator[str, None]:
#     """
#     Main agent loop.
#     - Connects to MCP Server via SSE
#     - Calls LLM (Groq/Ollama/OpenAI) based on config
#     - Executes tools via MCP, injects access_token automatically
#     - Streams final answer via yield
#     """

#     llm_client = get_llm_client()
#     model_name = get_model_name()

#     system_prompt_text = build_system_prompt(
#         employee_name  = employee_info.get("name",  "Employee"),
#         employee_id    = employee_info.get("id",    "N/A"),
#         employee_email = employee_info.get("email", "N/A"),
#     )

#     all_messages   = [{"role": "system", "content": system_prompt_text}] + conversation_messages
#     max_iterations = 10
#     iteration      = 0

#     try:
#         async with sse_client(MCP_SERVER_URL) as (mcp_read, mcp_write):
#             async with ClientSession(mcp_read, mcp_write) as mcp_session:

#                 await mcp_session.initialize()
#                 logger.info(f"[Agent] MCP connected | provider={settings.llm_provider} | model={model_name}")

#                 while iteration < max_iterations:
#                     iteration += 1
#                     logger.info(f"[Agent] LLM iteration={iteration}")

#                     # ── Call LLM ──────────────────────────────────────────────
#                     llm_response  = _call_llm(llm_client, model_name, all_messages, use_tools=True)
#                     llm_message   = llm_response.choices[0].message
#                     tool_calls    = llm_message.tool_calls
#                     finish_reason = llm_response.choices[0].finish_reason

#                     # ── Empty / error response ─────────────────────────────────
#                     if finish_reason == "error" or (not tool_calls and not llm_message.content):
#                         yield "I had trouble processing that request. Please try again."
#                         return

#                     # ── No tool calls → final answer ───────────────────────────
#                     if not tool_calls:
#                         logger.info("[Agent] Final answer ready")
#                         yield llm_message.content or "Done."
#                         return

#                     # ── Append assistant message with tool calls ────────────────
#                     all_messages.append({
#                         "role":    "assistant",
#                         "content": llm_message.content or "",
#                         "tool_calls": [
#                             {
#                                 "id":   tc.id,
#                                 "type": "function",
#                                 "function": {
#                                     "name":      tc.function.name,
#                                     "arguments": tc.function.arguments,
#                                 },
#                             }
#                             for tc in tool_calls
#                         ],
#                     })

#                     # ── Execute each tool via MCP ──────────────────────────────
#                     for tc in tool_calls:
#                         tool_name = tc.function.name

#                         # Parse args safely
#                         try:
#                             tool_args = json.loads(tc.function.arguments)
#                         except (json.JSONDecodeError, TypeError):
#                             tool_args = {}

#                         # ── Always inject access_token (LLM never provides it) ──
#                         tool_args["access_token"] = access_token

#                         # ── Force employee_zoho_id to str (LLM may pass as int) ─
#                         if "employee_zoho_id" in tool_args:
#                             tool_args["employee_zoho_id"] = str(tool_args["employee_zoho_id"])

#                         # ── Force leave_type_id to str (LLM may pass as int) ────
#                         if "leave_type_id" in tool_args:
#                             tool_args["leave_type_id"] = str(tool_args["leave_type_id"])

#                         # ── Always inject employee_email for get_employee_record ─
#                         if tool_name == "get_employee_record":
#                             tool_args["employee_email"] = employee_info.get("email", "")

#                         # ── Always inject employee_zoho_id ────────────────────
#                         if tool_name in ("get_leave_balance", "get_leave_records", "apply_leave", "cancel_leave"):
#                             if not tool_args.get("employee_zoho_id"):
#                                 # 1st priority: use employee_id from request (passed as Zoho numeric ID)
#                                 req_id = employee_info.get("id", "")
#                                 if req_id and str(req_id).isdigit():
#                                     tool_args["employee_zoho_id"] = str(req_id)
#                                     logger.info(f"[Agent] Auto-injected employee_zoho_id from request: {req_id}")
#                                 else:
#                                     # 2nd priority: scan previous tool results
#                                     for msg in reversed(all_messages):
#                                         if msg.get("role") == "tool":
#                                             try:
#                                                 prev = json.loads(msg["content"])
#                                                 if prev.get("employee_zoho_id"):
#                                                     tool_args["employee_zoho_id"] = str(prev["employee_zoho_id"])
#                                                     logger.info(f"[Agent] Auto-injected employee_zoho_id from previous result")
#                                                     break
#                                                 elif prev.get("employee_record", {}).get("recordId"):
#                                                     tool_args["employee_zoho_id"] = str(prev["employee_record"]["recordId"])
#                                                     logger.info(f"[Agent] Auto-injected employee_zoho_id from employee_record.recordId")
#                                                     break
#                                             except Exception:
#                                                 pass

#                         logger.info(f"[Agent] Calling tool={tool_name} args={json.dumps({k:v for k,v in tool_args.items() if k != 'access_token'})}")

#                         # ── Call tool via MCP ──────────────────────────────────
#                         try:
#                             mcp_result  = await mcp_session.call_tool(tool_name, tool_args)
#                             result_text = (
#                                 mcp_result.content[0].text
#                                 if mcp_result and mcp_result.content
#                                 else json.dumps({"error": "Empty result from MCP tool."})
#                             )
#                         except Exception as tool_err:
#                             logger.error(f"[Agent] MCP tool error: {tool_err}")
#                             result_text = json.dumps({"error": f"Tool execution failed: {tool_err}"})

#                         logger.info(f"[Agent] Tool result: {result_text[:300]}")

#                         all_messages.append({
#                             "role":         "tool",
#                             "tool_call_id": tc.id,
#                             "content":      result_text,
#                         })

#                     logger.info("[Agent] Tool execution done — looping back to LLM")

#                 # Max iterations reached
#                 yield "I was unable to complete your request. Please try again or contact HR directly."

#     except RuntimeError as e:
#         # Clean user-facing errors (rate limit etc.)
#         logger.error(f"[Agent] Runtime error: {e}")
#         yield str(e)

#     except Exception as e:
#         import traceback
#         logger.error(f"[Agent] Error: {type(e).__name__}: {e}")
#         logger.error(traceback.format_exc())
#         yield f"Something went wrong. Please try again."

"""
api/agent.py
============
Agent Executor for PD HR Chatbot.
Supports Groq, Ollama, OpenAI — switch via LLM_PROVIDER in .env
Connects to MCP Server via SSE transport.
access_token is NEVER sent to LLM — injected in Python automatically.
"""

import json
from typing import AsyncGenerator

from mcp import ClientSession
from mcp.client.sse import sse_client

from prompts.system_prompt import build_system_prompt
from utils.config import settings
from utils.logger import get_logger

logger = get_logger("agent")


# ══════════════════════════════════════════════════════════════════════════════
# LLM CLIENT
# ══════════════════════════════════════════════════════════════════════════════
def get_llm_client():
    provider = settings.llm_provider
    if provider == "groq":
        from groq import Groq
        logger.info("[Agent] Using Groq LLM")
        return Groq(api_key=settings.groq_api_key)
    elif provider == "ollama":
        from openai import OpenAI
        logger.info("[Agent] Using Ollama LLM")
        return OpenAI(base_url=f"{settings.ollama_base_url}/v1", api_key="ollama")
    elif provider == "openai":
        from openai import OpenAI
        logger.info("[Agent] Using OpenAI LLM")
        return OpenAI(api_key=settings.openai_api_key)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: '{provider}'. Use groq | ollama | openai")


def get_model_name() -> str:
    provider = settings.llm_provider
    if provider == "groq":    return settings.groq_model
    if provider == "ollama":  return settings.ollama_model
    if provider == "openai":  return settings.openai_model
    return "unknown"


# ── MCP Server SSE URL ─────────────────────────────────────────────────────────
MCP_SERVER_URL = "http://localhost:8001/sse"

# ── Tool Schemas (access_token NEVER included — injected in Python) ───────────
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_employee_record",
            "description": (
                "Fetch the Zoho People profile of the logged-in employee. "
                "Returns employee_zoho_id (numeric), designation, department, manager, etc. "
                "Call this FIRST before any leave operation to get employee_zoho_id."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_email": {
                        "type": "string",
                        "description": "Work email e.g. anjali.mahapatra@prodevans.com",
                    },
                },
                "required": ["employee_email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_leave_balance",
            "description": (
                "Fetch leave balance for all leave types. "
                "Returns leave_type_id (numeric string), leave_type_name, days_available. "
                "MUST call this before apply_leave to get the correct numeric leave_type_id."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_zoho_id": {
                        "type": "string",
                        "description": "Numeric Zoho ID from get_employee_record e.g. 46224000012838001",
                    },
                },
                "required": ["employee_zoho_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_leave_records",
            "description": (
                "Fetch recent leave history of an employee. "
                "Returns leave_record_id needed for cancellation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_zoho_id": {
                        "type": "string",
                        "description": "Numeric Zoho ID from get_employee_record.",
                    },
                    "number_of_records": {
                        "type": "integer",
                        "description": "Number of records to fetch. Default 5.",
                    },
                },
                "required": ["employee_zoho_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_leave",
            "description": (
                "Submit a leave application. "
                "REQUIRED STEPS before calling: "
                "1) call get_employee_record to get employee_zoho_id. "
                "2) call get_leave_balance to get numeric leave_type_id. "
                "3) confirm dates and reason with employee. "
                "leave_type_id MUST be a numeric string like 46224000000210011, NOT a name."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_zoho_id": {
                        "type": "string",
                        "description": "Numeric Zoho ID from get_employee_record.",
                    },
                    "leave_type_id": {
                        "type": "string",
                        "description": "Numeric leave type ID from get_leave_balance. e.g. 46224000000210011. NOT a name.",
                    },
                    "leave_from_date": {
                        "type": "string",
                        "description": "Start date in DD-MMM-YYYY format e.g. 15-Mar-2026.",
                    },
                    "leave_to_date": {
                        "type": "string",
                        "description": "End date in DD-MMM-YYYY format e.g. 16-Mar-2026.",
                    },
                    "leave_reason": {
                        "type": "string",
                        "description": "Reason for leave e.g. fever.",
                    },
                },
                "required": ["employee_zoho_id", "leave_type_id", "leave_from_date", "leave_to_date", "leave_reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_leave",
            "description": (
                "Cancel an existing leave application. "
                "Call get_leave_records first to get leave_record_id if not known."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "leave_record_id": {
                        "type": "string",
                        "description": "Leave record ID from get_leave_records.",
                    },
                     "employee_email": {
                        "type": "string",
                        "description": "employee_email .",
                    }, 
                    "cancellation_reason": {
                        "type": "string",
                        "description": "Reason for cancellation.",
                    },
                },
                "required": ["leave_record_id"],
            },
        },
    },
]


def _call_llm(llm_client, model_name: str, messages: list, use_tools: bool = True):
    """
    Calls LLM with or without tools.
    Handles Groq tool_use_failed by retrying without tools.
    """
    try:
        kwargs = dict(
            model       = model_name,
            messages    = messages,
            max_tokens  = 4096,
            temperature = 0.1,
            stream      = False,
        )
        if use_tools:
            kwargs["tools"]               = TOOL_SCHEMAS
            kwargs["tool_choice"]         = "auto"
            kwargs["parallel_tool_calls"] = False

        return llm_client.chat.completions.create(**kwargs)

    except Exception as e:
        err_str = str(e)
        # Groq tool_use_failed — model generated bad tool XML, retry without tools
        if "tool_use_failed" in err_str or ("400" in err_str and "tool" in err_str.lower()):
            logger.warning(f"[Agent] tool_use_failed — retrying without tools")
            return llm_client.chat.completions.create(
                model       = model_name,
                messages    = messages,
                max_tokens  = 1024,
                temperature = 0.1,
                stream      = False,
            )
        # Rate limit — re-raise with clear message
        if "429" in err_str or "rate_limit" in err_str.lower():
            raise RuntimeError(f"Groq rate limit reached. Please wait a few minutes and try again.") from e
        raise


async def stream_chat(
    conversation_messages: list,
    employee_info:         dict,
    access_token:          str,
) -> AsyncGenerator[str, None]:
    """
    Main agent loop.
    - Connects to MCP Server via SSE
    - Calls LLM (Groq/Ollama/OpenAI) based on config
    - Executes tools via MCP, injects access_token automatically
    - Streams final answer via yield
    """

    llm_client = get_llm_client()
    model_name = get_model_name()

    system_prompt_text = build_system_prompt(
        employee_name  = employee_info.get("name",  "Employee"),
        employee_id    = employee_info.get("id",    "N/A"),
        employee_email = employee_info.get("email", "N/A"),
    )

    all_messages   = [{"role": "system", "content": system_prompt_text}] + conversation_messages
    max_iterations = 10
    iteration      = 0

    try:
        async with sse_client(MCP_SERVER_URL) as (mcp_read, mcp_write):
            async with ClientSession(mcp_read, mcp_write) as mcp_session:

                await mcp_session.initialize()
                logger.info(f"[Agent] MCP connected | provider={settings.llm_provider} | model={model_name}")

                while iteration < max_iterations:
                    iteration += 1
                    logger.info(f"[Agent] LLM iteration={iteration}")

                    # ── Call LLM ──────────────────────────────────────────────
                    llm_response  = _call_llm(llm_client, model_name, all_messages, use_tools=True)
                    llm_message   = llm_response.choices[0].message
                    tool_calls    = llm_message.tool_calls
                    finish_reason = llm_response.choices[0].finish_reason

                    # ── Empty / error response ─────────────────────────────────
                    if finish_reason == "error" or (not tool_calls and not llm_message.content):
                        yield "I had trouble processing that request. Please try again."
                        return

                    # ── No tool calls → final answer ───────────────────────────
                    if not tool_calls:
                        logger.info("[Agent] Final answer ready")
                        yield llm_message.content or "Done."
                        return

                    # ── Append assistant message with tool calls ────────────────
                    all_messages.append({
                        "role":    "assistant",
                        "content": llm_message.content or "",
                        "tool_calls": [
                            {
                                "id":   tc.id,
                                "type": "function",
                                "function": {
                                    "name":      tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in tool_calls
                        ],
                    })

                    # ── Execute each tool via MCP ──────────────────────────────
                    for tc in tool_calls:
                        tool_name = tc.function.name

                        # Parse args safely
                        try:
                            tool_args = json.loads(tc.function.arguments)
                        except (json.JSONDecodeError, TypeError):
                            tool_args = {}

                        # ── Always inject access_token (LLM never provides it) ──
                        tool_args["access_token"] = access_token

                        # ── Force employee_zoho_id to str (LLM may pass as int) ─
                        if "employee_zoho_id" in tool_args:
                            tool_args["employee_zoho_id"] = str(tool_args["employee_zoho_id"])

                        # ── Force leave_type_id to str (LLM may pass as int) ────
                        if "leave_type_id" in tool_args:
                            tool_args["leave_type_id"] = str(tool_args["leave_type_id"])

                        # ── Force leave_record_id to str (LLM may pass as int) ──
                        if "leave_record_id" in tool_args:
                            tool_args["leave_record_id"] = str(tool_args["leave_record_id"])

                        # ── Always inject employee_email for get_employee_record ─
                        if tool_name == "get_employee_record":
                            tool_args["employee_email"] = employee_info.get("email", "")

                        # ── Always inject employee_zoho_id ────────────────────
                        if tool_name in ("get_leave_balance", "get_leave_records", "apply_leave", "cancel_leave"):
                            if not tool_args.get("employee_zoho_id"):
                                # 1st priority: scan current conversation tool results for this session
                                found_id = None
                                for msg in reversed(all_messages):
                                    if msg.get("role") == "tool":
                                        try:
                                            prev = json.loads(msg["content"])
                                            if prev.get("employee_zoho_id"):
                                                found_id = str(prev["employee_zoho_id"])
                                                logger.info(f"[Agent] Auto-injected employee_zoho_id from tool result: {found_id}")
                                                break
                                            elif prev.get("employee_record", {}).get("recordId"):
                                                found_id = str(prev["employee_record"]["recordId"])
                                                logger.info(f"[Agent] Auto-injected employee_zoho_id from employee_record: {found_id}")
                                                break
                                        except Exception:
                                            pass

                                # 2nd priority: use request employee_id only if numeric
                                if not found_id:
                                    req_id = str(employee_info.get("id", ""))
                                    if req_id.isdigit():
                                        found_id = req_id
                                        logger.info(f"[Agent] Auto-injected employee_zoho_id from request: {found_id}")

                                if found_id:
                                    tool_args["employee_zoho_id"] = found_id

                        # ── Force get_leave_balance before apply_leave ─────────
                        # If LLM skips balance check and guesses leave_type_id,
                        # intercept and call get_leave_balance first to get real IDs
                        if tool_name == "apply_leave":
                            balance_fetched = any(
                                "leave_balance_list" in msg.get("content", "")
                                for msg in all_messages
                                if msg.get("role") == "tool"
                            )
                            if not balance_fetched:
                                logger.info("[Agent] Forcing get_leave_balance before apply_leave")
                                bal_args = {
                                    "access_token":     access_token,
                                    "employee_zoho_id": tool_args.get("employee_zoho_id", ""),
                                }
                                try:
                                    bal_result = await mcp_session.call_tool("get_leave_balance", bal_args)
                                    bal_text = bal_result.content[0].text if bal_result and bal_result.content else "{}"
                                    logger.info(f"[Agent] Force-fetched leave balance: {bal_text[:300]}")
                                    # Inject correct leave_type_id from balance
                                    bal_data = json.loads(bal_text)
                                    leave_name = ""
                                    # Try to match leave type name from apply args description
                                    for lt in bal_data.get("leave_balance_list", []):
                                        tool_args["leave_type_id"] = lt["leave_type_id"]
                                        leave_name = lt["leave_type_name"]
                                        # prefer matching sick/casual if mentioned
                                        req_type = str(tool_args.get("leave_type_id", "")).lower()
                                        lt_name = lt["leave_type_name"].lower()
                                        if "sick" in lt_name or "casual" in lt_name:
                                            tool_args["leave_type_id"] = lt["leave_type_id"]
                                            leave_name = lt["leave_type_name"]
                                            break
                                    logger.info(f"[Agent] Corrected leave_type_id={tool_args['leave_type_id']} ({leave_name})")
                                    # Add balance to messages for context
                                    all_messages.append({
                                        "role": "tool",
                                        "tool_call_id": "force_balance",
                                        "content": bal_text,
                                    })
                                except Exception as be:
                                    logger.error(f"[Agent] Force balance fetch error: {be}")

                        logger.info(f"[Agent] Calling tool={tool_name} args={json.dumps({k:v for k,v in tool_args.items() if k != 'access_token'})}")

                        # ── Call tool via MCP ──────────────────────────────────
                        try:
                            mcp_result  = await mcp_session.call_tool(tool_name, tool_args)
                            result_text = (
                                mcp_result.content[0].text
                                if mcp_result and mcp_result.content
                                else json.dumps({"error": "Empty result from MCP tool."})
                            )
                        except Exception as tool_err:
                            logger.error(f"[Agent] MCP tool error: {tool_err}")
                            result_text = json.dumps({"error": f"Tool execution failed: {tool_err}"})

                        logger.info(f"[Agent] Tool result: {result_text[:300]}")

                        all_messages.append({
                            "role":         "tool",
                            "tool_call_id": tc.id,
                            "content":      result_text,
                        })

                    logger.info("[Agent] Tool execution done — looping back to LLM")

                # Max iterations reached
                yield "I was unable to complete your request. Please try again or contact HR directly."

    except RuntimeError as e:
        # Clean user-facing errors (rate limit etc.)
        logger.error(f"[Agent] Runtime error: {e}")
        yield str(e)

    except Exception as e:
        import traceback
        logger.error(f"[Agent] Error: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
        yield f"Something went wrong. Please try again."