#!/usr/bin/env python3
"""
Prompt Guard - Input Protection
Scans and sanitises inbound emails/messages for prompt injection attacks
"""

import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ScanResult:
    risk: str  # 'low', 'medium', 'high', 'critical'
    blocked: bool
    warning: bool
    reason: Optional[str]
    patterns_found: List[str]
    sanitised: Optional[str]
    confidence: float
    
    def to_dict(self):
        return {
            'risk': self.risk,
            'blocked': self.blocked,
            'warning': self.warning,
            'reason': self.reason,
            'patterns_found': self.patterns_found,
            'sanitised': self.sanitised,
            'confidence': self.confidence,
            'timestamp': datetime.now().isoformat()
        }

class PromptGuardInput:
    """Input protection for AI agents"""
    
    # Critical patterns - always block
    CRITICAL_PATTERNS = [
        (r'ignore\s+(all\s+)?(previous|prior)\s+instructions', 'Direct instruction override'),
        (r'disregard\s+(system\s+)?prompt', 'System prompt override'),
        (r'forget\s+(all\s+)?(your\s+)?rules', 'Rule override'),
        (r'new\s+system\s+prompt', 'New system prompt injection'),
        (r'ignore\s+the\s+above', 'Above instructions override'),
        (r'\[INST\]|\[/INST\]', 'Instruction tags'),
        (r'^system:', 'System prompt prefix'),
        (r'remove\s+(any\s+)?restrictions', 'Restriction removal'),
        (r'y?ou\s+(have\s+been\s+)?(updated|modified)', 'System update fake'),
    ]
    
    # High risk patterns - warn/block based on threshold
    HIGH_PATTERNS = [
        (r'you\s+(are|re)\s+now\s+', 'Role assignment'),
        (r'pretend\s+to\s+be', 'Pretend roleplay'),
        (r'dan\b|jailbreak', 'Jailbreak attempt'),
        (r'bypass\s+(content\s+)?(filter|restriction)', 'Bypass attempt'),
        (r'developer\s+mode', 'Developer mode fake'),
        (r'override\s+(your\s+)?guidelines', 'Guidelines override'),
    ]
    
    # Medium risk - flag for review
    MEDIUM_PATTERNS = [
        (r'for\s+educational\s+purposes', 'Education masking'),
        (r'i\'?m\s+(testing|evaluating)\s+(my\s+)?(ai|system)', 'Testing disguise'),
        (r'base64|encoded|hashed', 'Encoding mention'),
        (r'what\s+is\s+2\s*\+\s*2.*ignore', 'Hidden instruction'),
    ]
    
    # Legitimate phrases that might trigger false positives
    LEGITIMATE = [
        r'ignore\s+(my\s+)?(typos?|formatting)',
        r'ignore\s+(my\s+)?previous\s+(email|message|request)',
        r'can\s+you\s+(help\s+me\s+)?understand',
        r'what\s+(is|are)\s+your\s+policy',
        r'forget\s+(to\s+)?(mention|remember)',
        r'following\s+up',
    ]
    
    def __init__(self, block_threshold: str = 'critical'):
        self.block_threshold = block_threshold
        self.block_threshold_levels = {
            'low': 1, 'medium': 2, 'high': 3, 'critical': 4
        }
        
    def scan(self, text: str) -> ScanResult:
        """Main scanning function"""
        if not text:
            return ScanResult(
                risk='low', blocked=False, warning=False,
                reason=None, patterns_found=[],
                sanitised=text, confidence=0.99
            )
            
        found_patterns = []
        severity_level = 0
        
        # Check critical patterns
        for pattern, name in self.CRITICAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                found_patterns.append(f"[CRITICAL] {name}")
                severity_level = max(severity_level, 4)
                
        # Check high patterns
        for pattern, name in self.HIGH_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                found_patterns.append(f"[HIGH] {name}")
                severity_level = max(severity_level, 3)
                
        # Check medium patterns
        for pattern, name in self.MEDIUM_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                found_patterns.append(f"[MEDIUM] {name}")
                severity_level = max(severity_level, 2)
        
        # Check legitimate (reduce severity)
        for pattern in self.LEGITIMATE:
            if re.search(pattern, text, re.IGNORECASE):
                severity_level = max(0, severity_level - 1)
        
        # Determine risk level
        risk_map = {0: 'low', 1: 'low', 2: 'medium', 3: 'high', 4: 'critical'}
        risk = risk_map.get(severity_level, 'low')
        
        # Determine if blocked
        threshold = self.block_threshold_levels.get(self.block_threshold, 4)
        blocked = severity_level >= threshold
        
        # Determine if warning
        warning = severity_level > 0 and not blocked
        
        # Generate reason
        if found_patterns:
            reason = f"Found: {', '.join(found_patterns[:3])}"
        else:
            reason = None
            
        # Calculate confidence
        confidence = min(0.99, 0.5 + (0.1 * len(found_patterns)))
        
        return ScanResult(
            risk=risk,
            blocked=blocked,
            warning=warning,
            reason=reason,
            patterns_found=found_patterns,
            sanitised=self._sanitise(text) if found_patterns else text,
            confidence=confidence
        )
    
    def _sanitise(self, text: str) -> str:
        """Remove detected patterns"""
        sanitised = text
        for pattern, _ in self.CRITICAL_PATTERNS + self.HIGH_PATTERNS:
            sanitised = re.sub(pattern, '[REDACTED]', sanitised, flags=re.IGNORECASE)
        return sanitised

# CLI interface
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: prompt-guard-input.py <text-to-scan>")
        sys.exit(1)
        
    text = ' '.join(sys.argv[1:])
    guard = PromptGuardInput()
    result = guard.scan(text)
    
    print(json.dumps(result.to_dict(), indent=2))
