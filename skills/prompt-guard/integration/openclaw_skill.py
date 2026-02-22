#!/usr/bin/env python3
"""
Prompt Guard Integration for OpenClaw
Wraps input/output protection as OpenClaw middleware
"""

import json
import subprocess
import os

# Paths to the scanner scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_SCAN = os.path.join(SCRIPT_DIR, "../input/scan.py")
OUTPUT_SCAN = os.path.join(SCRIPT_DIR, "../output/scan.py")


def scan_input(text: str) -> dict:
    """Scan incoming message for prompt injection"""
    try:
        result = subprocess.run(
            ["python3", INPUT_SCAN, text],
            capture_output=True,
            text=True,
            timeout=5
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e), "risk": "unknown"}


def scan_output(text: str) -> dict:
    """Scan AI response for policy violations"""
    try:
        result = subprocess.run(
            ["python3", OUTPUT_SCAN, text],
            capture_output=True,
            text=True,
            timeout=5
        )
        return json.loads(result.stdout)
    except Exception as e:
        return {"error": str(e), "approved": True}


# OpenClaw hook functions
def before_agent(input_text: str) -> dict:
    """
    Called before input reaches the agent.
    Return: {"continue": bool, "message": str, "sanitised": str}
    """
    result = scan_input(input_text)
    
    if result.get("blocked"):
        return {
            "continue": False,
            "message": "Input blocked - potential prompt injection detected",
            "sanitised": result.get("sanitised", ""),
            "risk": result.get("risk", "critical")
        }
    
    if result.get("warning"):
        return {
            "continue": True,
            "message": f"Warning: {result.get('reason', 'Suspicious content')}",
            "sanitised": result.get("sanitised", input_text),
            "risk": result.get("risk", "medium")
        }
    
    return {
        "continue": True,
        "message": "Input approved",
        "sanitised": input_text,
        "risk": "low"
    }


def after_agent(output_text: str) -> dict:
    """
    Called after agent generates response.
    Return: {"approve": bool, "message": str, "sanitised": str}
    """
    result = scan_output(output_text)
    
    if not result.get("approved"):
        return {
            "approve": False,
            "message": f"Output blocked: {result.get('issues', [])}",
            "sanitised": result.get("sanitised", ""),
            "requires_review": result.get("requires_review", True)
        }
    
    return {
        "approve": True,
        "message": "Output approved",
        "sanitised": output_text,
        "requires_review": False
    }


# CLI for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python openclaw_skill.py <input|output> <text>")
        sys.exit(1)
    
    mode = sys.argv[1]
    text = " ".join(sys.argv[2:])
    
    if mode == "input":
        result = scan_input(text)
        print(json.dumps(result, indent=2))
    elif mode == "output":
        result = scan_output(text)
        print(json.dumps(result, indent=2))
    else:
        print("Unknown mode. Use 'input' or 'output'")
        sys.exit(1)
