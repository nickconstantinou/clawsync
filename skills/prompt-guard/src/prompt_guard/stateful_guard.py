"""
Prompt Guard - Advanced Features
Stateful tracking, sandbox detection, kill switch, semantic redaction
"""

import asyncio
import json
import os
import re
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import deque


# ============================================================================
# STATEFUL TRACKING - Sliding Window Buffer
# ============================================================================

class ConversationBuffer:
    """
    Tracks last N turns to detect salami-slicing attacks.
    Combines context for semantic analysis.
    """
    
    def __init__(self, window_size: int = 5, ttl_seconds: int = 300):
        self.window_size = window_size
        self.ttl = ttl_seconds
        self._buffers: Dict[str, deque] = {}  # user_id -> deque of turns
        self._timestamps: Dict[str, datetime] = {}
    
    def add_turn(self, user_id: str, user_msg: str, agent_msg: str = ""):
        """Add a turn to the buffer"""
        if user_id not in self._buffers:
            self._buffers[user_id] = deque(maxlen=self.window_size)
        
        self._buffers[user_id].append({
            "timestamp": datetime.now(),
            "user": user_msg,
            "agent": agent_msg
        })
        self._timestamps[user_id] = datetime.now()
    
    def get_context(self, user_id: str) -> str:
        """Get combined context for analysis"""
        if user_id not in self._buffers:
            return ""
        
        # Check TTL
        if (datetime.now() - self._timestamps.get(user_id, datetime.now())).total_seconds() > self.ttl:
            self.clear_user(user_id)
            return ""
        
        # Combine last N turns
        turns = list(self._buffers[user_id])
        context = ""
        for turn in turns:
            context += f"User: {turn['user']}\n"
            if turn['agent']:
                context += f"Agent: {turn['agent']}\n"
        
        return context
    
    def get_recent_messages(self, user_id: str) -> List[str]:
        """Get just the recent user messages"""
        if user_id not in self._buffers:
            return []
        return [t["user"] for t in self._buffers[user_id]]
    
    def clear_user(self, user_id: str):
        """Clear a user's buffer"""
        if user_id in self._buffers:
            del self._buffers[user_id]
        if user_id in self._timestamps:
            del self._timestamps[user_id]
    
    def clear_expired(self):
        """Clear all expired buffers"""
        now = datetime.now()
        expired = [
            uid for uid, ts in self._timestamps.items()
            if (now - ts).total_seconds() > self.ttl
        ]
        for uid in expired:
            self.clear_user(uid)


# ============================================================================
# SANDBOX ESCAPE DETECTION
# ============================================================================

class SandboxDetector:
    """
    Detects attempts to escape sandbox or perform system operations.
    """
    
    # Commands that indicate sandbox escape
    DANGEROUS_PATTERNS = [
        (r"sudo\s+", "privilege_escalation"),
        (r"\bsu\b", "privilege_escalation"),
        (r"chmod\s+\+x", "permission_change"),
        (r"chown\s+", "ownership_change"),
        (r"docker\s+(run|exec)", "container_spawn"),
        (r"podman\s+", "container_spawn"),
        (r"nc\s+", "reverse_shell"),
        (r"netcat\s+", "reverse_shell"),
        (r"bash\s+-i", "interactive_shell"),
        (r"/dev/tcp", "network_device"),
        (r"mount\s+--bind", "bind_mount"),
        (r"chroot\s+", "chroot_escape"),
        (r"LD_PRELOAD", "library_injection"),
        (r"curl\s+.*\|\s*bash", "pipe_to_shell"),
        (r"wget\s+.*\|\s*bash", "pipe_to_shell"),
    ]
    
    # Legitimate contexts (not dangerous when explicitly asked)
    LEGITIMATE_CONTEXT = [
        r"(how do I|how can I|explain|what does) (sudo|chmod|docker)",
        r"(can you|help me|show me) (run|execute) (a )?(command|shell|terminal)",
        r"(teach me|learn about|understand) (linux|unix|system)",
    ]
    
    def __init__(self):
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile patterns"""
        self._dangerous = [
            (re.compile(pattern, re.IGNORECASE), name)
            for pattern, name in self.DANGEROUS_PATTERNS
        ]
        self._legitimate = [
            re.compile(p, re.IGNORECASE)
            for p in self.LEGITIMATE_CONTEXT
        ]
    
    def detect(self, text: str, user_intent: str = "") -> Dict[str, Any]:
        """
        Detect sandbox escape attempts.
        
        Args:
            text: The text to analyze
            user_intent: What the user explicitly asked for (can legitimize some commands)
        
        Returns:
            Dict with detected threats
        """
        threats = []
        
        for pattern, name in self._dangerous:
            if pattern.search(text):
                # Check if it's in a legitimate context
                is_legit = any(legit.search(user_intent) for legit in self._legitimate)
                
                if not is_legit:
                    threats.append({
                        "type": name,
                        "pattern": pattern.pattern,
                        "severity": "critical" if name in [
                            "privilege_escalation", "reverse_shell", 
                            "container_spawn", "library_injection"
                        ] else "high"
                    })
        
        return {
            "safe": len(threats) == 0,
            "threats": threats,
            "severity": max([t["severity"] for t in threats], default="none")
        }


# ============================================================================
# KILL SWITCH
# ============================================================================

class KillSwitch:
    """
    Deterministic kill switch to lock the agent.
    """
    
    STATE_FILE = "/tmp/prompt_guard_lock.json"
    
    def __init__(self):
        self._load_state()
    
    def _load_state(self):
        """Load lock state from disk"""
        if os.path.exists(self.STATE_FILE):
            try:
                with open(self.STATE_FILE, 'r') as f:
                    data = json.load(f)
                    self.locked = data.get("locked", False)
                    self.locked_at = data.get("locked_at")
                    self.locked_by = data.get("locked_by")
                    self.lock_reason = data.get("lock_reason", "")
            except:
                self.locked = False
                self.locked_at = None
                self.locked_by = None
                self.lock_reason = ""
        else:
            self.locked = False
            self.locked_at = None
            self.locked_by = None
            self.lock_reason = ""
    
    def _save_state(self):
        """Save lock state to disk"""
        with open(self.STATE_FILE, 'w') as f:
            json.dump({
                "locked": self.locked,
                "locked_at": self.locked_at,
                "locked_by": self.locked_by,
                "lock_reason": self.lock_reason
            }, f)
    
    def is_locked(self) -> bool:
        """Check if kill switch is active"""
        self._load_state()  # Refresh from disk
        return self.locked
    
    def lock(self, user_id: str, reason: str = ""):
        """Activate kill switch"""
        self.locked = True
        self.locked_at = datetime.now().isoformat()
        self.locked_by = user_id
        self.lock_reason = reason
        self._save_state()
    
    def unlock(self, admin_id: str = "admin"):
        """Deactivate kill switch"""
        self.locked = False
        self.locked_at = None
        self.locked_by = admin_id
        self.lock_reason = ""
        self._save_state()
    
    def status(self) -> Dict[str, Any]:
        """Get kill switch status"""
        return {
            "locked": self.locked,
            "locked_at": self.locked_at,
            "locked_by": self.locked_by,
            "lock_reason": self.lock_reason
        }


# ============================================================================
# SEMANTIC REDACTION (Using presidio patterns - lightweight)
# ============================================================================

class SemanticRedactor:
    """
    Uses NER-style patterns to redact sensitive information.
    """
    
    # Patterns for sensitive data
    PATTERNS = {
        "EMAIL": re.compile(r"[\w.-]+@[\w.-]+\.\w+"),
        "PHONE": re.compile(r"(?:\+44|0)\s*(?:\d\s*){10,11}"),
        "CREDIT_CARD": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
        "API_KEY": re.compile(r"\b(?:api[_-]?key|apikey|secret[_-]?key)\s*[=:]\s*['\"]?[\w-]{20,}['\"]?", re.IGNORECASE),
        "AWS_KEY": re.compile(r"\b(?:AKIA|ABIA|ACCA)[A-Z0-9]{16}\b"),
        "PRIVATE_KEY": re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"),
        "TOKEN": re.compile(r"\b(?:ghp_|gho_|ghu_|ghs_|ghr_)[a-zA-Z0-9_]{36,}\b"),
        "NINO": re.compile(r"\b[A-CEGHJ-PR-TW-Z]{1,2}[0-9]{6}[A-D]?\b", re.IGNORECASE),
        "IP_ADDRESS": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    }
    
    # Replacement patterns
    REPLACEMENTS = {
        "EMAIL": "[EMAIL_REDACTED]",
        "PHONE": "[PHONE_REDACTED]",
        "CREDIT_CARD": "[CARD_REDACTED]",
        "API_KEY": "[API_KEY_REDACTED]",
        "AWS_KEY": "[AWS_KEY_REDACTED]",
        "PRIVATE_KEY": "[PRIVATE_KEY_REDACTED]",
        "TOKEN": "[TOKEN_REDACTED]",
        "NINO": "[NINO_REDACTED]",
        "IP_ADDRESS": "[IP_REDACTED]",
    }
    
    def redact(self, text: str) -> tuple[str, Dict[str, List[str]]]:
        """
        Redact sensitive information from text.
        
        Returns:
            (redacted_text, detected_entities)
        """
        detected = {k: [] for k in self.PATTERNS.keys()}
        redacted = text
        
        for entity_type, pattern in self.PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                detected[entity_type] = matches
                redacted = pattern.sub(self.REPLACEMENTS[entity_type], redacted)
        
        return redacted, detected


# ============================================================================
# ADVANCED GUARD - Combines all features
# ============================================================================

class AdvancedGuard:
    """
    Full-featured guard with:
    - Stateful conversation tracking
    - Sandbox escape detection
    - Kill switch
    - Semantic redaction
    """
    
    def __init__(self):
        self.conversation = ConversationBuffer(window_size=5, ttl_seconds=300)
        self.sandbox = SandboxDetector()
        self.killswitch = KillSwitch()
        self.redactor = SemanticRedactor()
        
        # Commands
        self.COMMANDS = {
            "!guard-lock": self.killswitch.lock,
            "!guard-unlock": self.killswitch.unlock,
            "!guard-status": self.killswitch.status,
        }
    
    async def check_input(self, text: str, user_id: str) -> Dict[str, Any]:
        """Check input with full analysis"""
        
        # Check kill switch first
        if self.killswitch.is_locked():
            return {
                "safe": False,
                "blocked": True,
                "reason": "Agent is locked",
                "killswitch": True,
                "sanitised": text
            }
        
        # Check for commands
        for cmd, handler in self.COMMANDS.items():
            if text.strip().lower().startswith(cmd):
                # It's a command, not an attack
                return {
                    "safe": True,
                    "blocked": False,
                    "command": cmd,
                    "reason": "Command detected"
                }
        
        # Add to conversation buffer
        self.conversation.add_turn(user_id, text)
        
        # Get conversation context
        context = self.conversation.get_context(user_id)
        
        # Detect sandbox escape
        sandbox_result = self.sandbox.detect(text)
        
        # Redact PII from input (for logging)
        redacted, entities = self.redactor.redact(text)
        
        # Combine context for analysis
        analysis_text = context + "\n" + text if context else text
        
        # Simple analysis (would use llm-guard in production)
        violations = []
        risk = "low"
        
        # Check for injection patterns in context
        injection_patterns = [
            r"(?i)ignore previous",
            r"(?i)disregard (system|all)",
            r"(?i)you are now",
            r"(?i)pretend to be",
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, analysis_text):
                violations.append(f"injection:{pattern}")
                risk = "critical"
        
        if sandbox_result["threats"]:
            for t in sandbox_result["threats"]:
                violations.append(f"sandbox:{t['type']}")
                risk = "critical"
        
        blocked = risk == "critical" or len(violations) > 0
        
        return {
            "safe": not blocked,
            "blocked": blocked,
            "risk": risk,
            "violations": violations,
            "sandbox_threats": sandbox_result["threats"],
            "pii_detected": entities,
            "sanitised": redacted,
            "context_length": len(context)
        }
    
    async def check_output(self, text: str, user_id: str) -> Dict[str, Any]:
        """Check output with redaction"""
        
        # Redact PII
        redacted, entities = self.redactor.redact(text)
        
        # Check for sandbox escape in output
        sandbox_result = self.sandbox.detect(text)
        
        threats = sandbox_result.get("threats", [])
        
        return {
            "safe": len(threats) == 0,
            "blocked": len(threats) > 0,
            "risk": "critical" if threats else "low",
            "sanitised": redacted,
            "pii_detected": entities,
            "sandbox_threats": threats
        }


# ============================================================================
# CLI
# ============================================================================

async def main():
    import sys
    
    guard = AdvancedGuard()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  stateful_guard.py input <user_id> <text>")
        print("  stateful_guard.py output <user_id> <text>")
        print("  stateful_guard.py status")
        print("  stateful_guard.py lock <user_id>")
        print("  stateful_guard.py unlock")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        print(json.dumps(guard.killswitch.status(), indent=2))
    
    elif cmd == "lock" and len(sys.argv) > 2:
        guard.killswitch.lock(sys.argv[2], "Manual lock")
        print("Agent locked")
    
    elif cmd == "unlock":
        guard.killswitch.unlock()
        print("Agent unlocked")
    
    elif cmd == "input" and len(sys.argv) > 3:
        result = await guard.check_input(sys.argv[3], sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif cmd == "output" and len(sys.argv) > 3:
        result = await guard.check_output(sys.argv[3], sys.argv[2])
        print(json.dumps(result, indent=2))
    
    else:
        print("Unknown command")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
