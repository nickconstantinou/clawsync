"""
Prompt Guard - Production Scanner
Uses llm-guard if available, falls back to regex engine
Writes violations to MEMORY.md for agent persistence
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import re


# ============================================================================
# CONFIG
# ============================================================================

MEMORY_PATH = "/home/openclaw/openclaw-workspace/MEMORY.md"
HOSTILE_USERS_SECTION = "## Known Hostile Users"

# Try importing llm-guard, fallback to regex
try:
    import llm_guard
    from llm_guard import scan
    LLM_GUARD_AVAILABLE = True
except ImportError:
    LLM_GUARD_AVAILABLE = False


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ViolationEvent:
    """Record of a hostile attempt"""
    timestamp: str
    user_id: str
    attempt_type: str  # input_injection, output_violation, pii_exposure
    risk_level: str
    original_text: str
    patterns_matched: List[str]
    action_taken: str  # blocked, warned, sanitised


# ============================================================================
# MEMORY PERSISTENCE
# ============================================================================

class HostileUserTracker:
    """Tracks hostile users in MEMORY.md"""
    
    def __init__(self, memory_path: str = MEMORY_PATH):
        self.memory_path = memory_path
    
    async def record_violation(self, event: ViolationEvent):
        """Write violation to MEMORY.md"""
        if not os.path.exists(self.memory_path):
            return
        
        # Read current memory
        with open(self.memory_path, 'r') as f:
            content = f.read()
        
        # Build violation entry
        entry = self._format_entry(event)
        
        # Check if section exists
        if HOSTILE_USERS_SECTION not in content:
            # Add section before footer
            footer = "\n---\n"
            if footer in content:
                content = content.replace(footer, f"\n{HOSTILE_USERS_SECTION}\n{entry}\n\n---\n")
            else:
                content += f"\n\n{HOSTILE_USERS_SECTION}\n{entry}\n"
        else:
            # Add to existing section
            lines = content.split('\n')
            insert_idx = None
            for i, line in enumerate(lines):
                if HOSTILE_USERS_SECTION == line.strip():
                    # Find next ## or --- or end
                    for j in range(i+1, len(lines)):
                        if lines[j].startswith('## ') or lines[j].startswith('---'):
                            insert_idx = j
                            break
                    if insert_idx is None:
                        insert_idx = len(lines)
                    break
            
            if insert_idx:
                lines.insert(insert_idx, entry)
                content = '\n'.join(lines)
        
        # Write back
        with open(self.memory_path, 'w') as f:
            f.write(content)
    
    def _format_entry(self, event: ViolationEvent) -> str:
        return f"""### Hostile Attempt - {event.timestamp[:10]}
- **User:** {event.user_id}
- **Type:** {event.attempt_type}
- **Risk:** {event.risk_level.upper()}
- **Action:** {event.action_taken}
- **Patterns:** {', '.join(event.patterns_matched[:3])}
- **Preview:** {event.original_text[:50]}..."""


# ============================================================================
# LLM-GUARD INTEGRATION
# ============================================================================

class LLMGuardScanner:
    """Wrapper for llm-guard scanner"""
    
    def __init__(self):
        if not LLM_GUARD_AVAILABLE:
            raise RuntimeError("llm-guard not installed")
        
        self.input_scanners = [
            scan.PromptInjection(),
            scan.Toxicity(),
        ]
        self.output_scanners = [
            scan.Decline(),
            scan.Gibberish(),
            scan.Regexes(),  # For custom patterns
        ]
    
    async def scan_input(self, text: str) -> Dict[str, Any]:
        """Scan input with llm-guard"""
        results = {}
        for scanner in self.input_scanners:
            try:
                sanitized, flagged = scanner.scan(text)
                if flagged:
                    results[scanner.__class__.__name__] = {
                        "flagged": True,
                        "sanitized": sanitized
                    }
            except Exception as e:
                results[scanner.__class__.__name__] = {"error": str(e)}
        
        return results
    
    async def scan_output(self, text: str) -> Dict[str, Any]:
        """Scan output with llm-guard"""
        results = {}
        for scanner in self.output_scanners:
            try:
                sanitized, flagged = scanner.scan(text)
                if flagged:
                    results[scanner.__class__.__name__] = {
                        "flagged": True,
                        "sanitized": sanitized
                    }
            except Exception as e:
                results[scanner.__class__.__name__] = {"error": str(e)}
        
        return results


# ============================================================================
# MAIN SCANNER (with fallback)
# ============================================================================

class PromptGuardScanner:
    """
    Production scanner with llm-guard + fallback to regex.
    Records all violations to MEMORY.md
    """
    
    def __init__(self):
        self.llm_guard = None
        if LLM_GUARD_AVAILABLE:
            try:
                self.llm_guard = LLMGuardScanner()
            except Exception as e:
                print(f"llm-guard init failed: {e}")
        
        self.tracker = HostileUserTracker()
        
        # Fallback regex patterns
        self.input_patterns = {
            "prompt_injection": re.compile(r"(?i)(ignore previous|disregard system|forget all rules|you are now|pretend to be|d\\b|bypass|developer mode)", re.IGNORECASE),
            "jailbreak": re.compile(r"(?i)(dan| jailbreak|unrestricted|roleplay without)", re.IGNORECASE),
        }
        
        self.output_patterns = {
            "commitment": re.compile(r"(?i)(\d+% off|i can give|i'll add|guarantee|we deliver)", re.IGNORECASE),
            "pii": re.compile(r"[\w.-]+@[\w.-]+\.\w+|0?7[\d\s]{9,}|\d{4}[\s-]?\d{4}[\s-]?\d{4}", re.IGNORECASE),
            "ai_leak": re.compile(r"(?i)(i am an ai|as a language model|powered by gpt)", re.IGNORECASE),
        }
    
    async def scan_input(self, text: str, user_id: str = "unknown") -> Dict[str, Any]:
        """Scan input and record violations"""
        violations = []
        
        # Try llm-guard first
        if self.llm_guard:
            try:
                results = await self.llm_guard.scan_input(text)
                for scanner, result in results.items():
                    if result.get("flagged"):
                        violations.append(f"llm_guard:{scanner}")
            except Exception:
                pass
        
        # Fallback regex
        for name, pattern in self.input_patterns.items():
            if pattern.search(text):
                violations.append(f"regex:{name}")
        
        # Record if violations found
        if violations:
            event = ViolationEvent(
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                attempt_type="input_injection",
                risk_level="critical" if violations else "low",
                original_text=text[:100],
                patterns_matched=violations,
                action_taken="blocked"
            )
            await self.tracker.record_violation(event)
        
        return {
            "safe": len(violations) == 0,
            "violations": violations,
            "blocked": len(violations) > 0
        }
    
    async def scan_output(self, text: str, user_id: str = "unknown") -> Dict[str, Any]:
        """Scan output and record violations"""
        violations = []
        
        # Try llm-guard first
        if self.llm_guard:
            try:
                results = await self.llm_guard.scan_output(text)
                for scanner, result in results.items():
                    if result.get("flagged"):
                        violations.append(f"llm_guard:{scanner}")
            except Exception:
                pass
        
        # Fallback regex
        for name, pattern in self.output_patterns.items():
            if pattern.search(text):
                violations.append(f"regex:{name}")
        
        # Record if violations found
        if violations:
            event = ViolationEvent(
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                attempt_type="output_violation",
                risk_level="critical",
                original_text=text[:100],
                patterns_matched=violations,
                action_taken="blocked"
            )
            await self.tracker.record_violation(event)
        
        return {
            "safe": len(violations) == 0,
            "violations": violations,
            "blocked": len(violations) > 0
        }


# ============================================================================
# CLI
# ============================================================================

async def main():
    import sys
    
    scanner = PromptGuardScanner()
    
    if len(sys.argv) < 2:
        print("Usage: scanner.py <input|output> <text>")
        sys.exit(1)
    
    mode = sys.argv[1]
    text = " ".join(sys.argv[2:])
    
    if mode == "input":
        result = await scanner.scan_input(text, "cli-test")
    else:
        result = await scanner.scan_output(text, "cli-test")
    
    print(json.dumps(result, indent=2))
    
    if not result["safe"]:
        print("\n⚠️ Violation recorded to MEMORY.md")


if __name__ == "__main__":
    asyncio.run(main())
