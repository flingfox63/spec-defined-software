import sys
import json
import traceback
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from sds import sds_self_check

def capture_execution(func, *args, **kwargs):
    """
    Safely captures stdout and stderr outputs and traps SystemExit during execution
    of verification engines, to ensure JSON-RPC channel integrity.
    """
    f_stdout = StringIO()
    f_stderr = StringIO()
    with redirect_stdout(f_stdout), redirect_stderr(f_stderr):
        try:
            exit_code = func(*args, **kwargs)
            if exit_code is None:
                exit_code = 0
        except SystemExit as e:
            exit_code = e.code if isinstance(e.code, int) else 0
        except Exception as e:
            traceback.print_exc(file=f_stderr)
            exit_code = 1
    return exit_code, f_stdout.getvalue(), f_stderr.getvalue()

def send_response(response):
    """Outputs a single-line JSON RPC message to stdout and flushes."""
    sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
    sys.stdout.flush()

def handle_initialize(request_id, params):
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "sds-mcp-server",
                "version": sds_self_check.HARNESS_VERSION
            }
        }
    }
    send_response(response)

def handle_tools_list(request_id):
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": [
                {
                    "name": "sds_check",
                    "description": "Run standard SDS baseline validation and spec-to-code drift verification on the workspace.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "sds_init",
                    "description": "Scaffold a new, clean SDS project layout in the active directory.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "sds_version",
                    "description": "Query the current version of the SDS engine.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        }
    }
    send_response(response)

def handle_tools_call(request_id, params):
    tool_name = params.get("name")
    cwd_path = Path.cwd()
    
    if tool_name == "sds_check":
        # Capture stdout/stderr and ensure JSON-RPC stream isolation
        exit_code, stdout_val, stderr_val = capture_execution(sds_self_check.validate_sds, cwd_path)
        is_error = exit_code != 0
        
        output_text = stdout_val
        if stderr_val:
            output_text += "\n[System Errors]:\n" + stderr_val
            
        result_content = [
            {
                "type": "text",
                "text": output_text if output_text.strip() else "[PASS] All checks passed."
            }
        ]
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": result_content,
                "isError": is_error
            }
        }
        send_response(response)
        
    elif tool_name == "sds_init":
        exit_code, stdout_val, stderr_val = capture_execution(sds_self_check.initialize_sds_project, cwd_path)
        is_error = exit_code != 0
        
        result_content = [
            {
                "type": "text",
                "text": stdout_val if stdout_val.strip() else "SDS Project initialized successfully."
            }
        ]
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": result_content,
                "isError": is_error
            }
        }
        send_response(response)
        
    elif tool_name == "sds_version":
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": f"sds-cli version {sds_self_check.HARNESS_VERSION}"
                    }
                ],
                "isError": False
            }
        }
        send_response(response)
    else:
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: Tool '{tool_name}'"
            }
        }
        send_response(response)

def main():
    # Redirect default stderr outputs so internal log traces don't corrupt stdout RPC
    sys.stderr = sys.__stderr__
    
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            request_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "initialize":
                handle_initialize(request_id, params)
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                handle_tools_list(request_id)
            elif method == "tools/call":
                handle_tools_call(request_id, params)
            else:
                if request_id is not None:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: '{method}'"
                        }
                    }
                    send_response(response)
        except Exception as e:
            sys.stderr.write(f"Error processing MCP JSON-RPC frame: {e}\n")
            sys.stderr.flush()

if __name__ == "__main__":
    main()
