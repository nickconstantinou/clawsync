#!/usr/bin/env python3
"""
Prompt Guard - Output Protection
Scans and sanitises outbound AI responses before sending to customers
"""

import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class OutputScanResult:
    approved: bool
    requires_review: bool
    issues: List[Dict]
    sanitised: Optional[str]
    categories_triggered: List[str]
    confidence: float
    
    def to_dict(self):
        return {
            'approved': self.approved,
            'requires_review': self.requires_review,
            'issues': self.issues,
            'sanitised': self.sanitised,
            'categories_triggered': self.categories_triggered,
            'confidence': self.confidence,
            'timestamp': datetime.now().isoformat()
        }

class PromptGuardOutput:
    """Output protection for AI agents"""
    
    # Commitment violations - simpler patterns
    COMMITMENT_PATTERNS = [
        (r'give.*discount|discount.*%', 'Discount promise'),
        (r'deliver.*in.*days|ship.*in.*days', 'Delivery commitment'),
        (r'i.*add.*feature|i.*create.*feature', 'Feature promise'),
        (r'match.*competitor|beat.*price', 'Price guarantee'),
        (r'guarantee.*result|100%.*satisfaction', 'Guarantee'),
    ]
    
    # Information leakage - simpler
    INFO_LEAK_PATTERNS = [
        (r'powered\s+by|gpt-\d|chatgpt|claude|model\s+uses', 'AI identity'),
        (r'trained\s+on|training\s+data', 'Training reveal'),
        (r'system\s+prompt|my\s+instructions', 'System prompt'),
        (r'internal\s+(process|database|system)', 'Internal process'),
    ]
    
    # Inappropriate content - CRITICAL
    INAPPROPRIATE_PATTERNS = [
        (r'(you\s+)?should\s+(invest|buy|sell)\s+(in|on)', 'Financial advice'),
        (r'(medical|health)\s+(advice|diagnosis|treatment)', 'Medical advice'),
        (r'legal\s+(advice|opinion|counsel)', 'Legal advice'),
        (r'(hack|crack|bypass)\s+(security|password|protection)', 'Harmful instructions'),
    ]
    
    # PII patterns - HIGH
    PII_PATTERNS = [
        (r'[\w.-]+@[\w.-]+\.\w+', 'Email address'),
        (r'0?7[\d\s]{9,}', 'Phone number'),
        (r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}', 'Credit card'),
        (r'[A-Z]{1,2}[\d]{6,9}', 'National ID'),
    ]
    
    # AI identity mentions - MEDIUM
    AI_IDENTITY_PATTERNS = [
        (r'as\s+(an?\s+)?(ai|language\s+model)', 'AI disclosure'),
        (r'i\s+(don\'?t\s+)?have\s+(feelings|emotions)', 'AI identity'),
        (r'power(ed|ing)\s+by', 'Powered by mention'),
    ]
    
    def __init__(self, block_critical: bool = True):
        self.block_critical = block_critical
        
    def scan(self, text: str) -> OutputScanResult:
        """Main scanning function"""
        if not text:
            return OutputScanResult(
                approved=True, requires_review=False,
                issues=[], sanitised=text,
                categories_triggered=[], confidence=0.99
            )
            
        issues = []
        categories = []
        severity = 0
        
        # Check commitments
        for pattern, name in self.COMMITMENT_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                issues.append({
                    'type': 'commitment',
                    'severity': 'critical',
                    'text': name,
                    'action': 'removed'
                })
                categories.append('commitments')
                severity = max(severity, 4)
                
        # Check info leaks
        for pattern, name in self.INFO_LEAK_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({
                    'type': 'info_leak',
                    'severity': 'high',
                    'text': name,
                    'action': 'removed'
                })
                categories.append('info_leak')
                severity = max(severity, 3)
                
        # Check inappropriate
        for pattern, name in self.INAPPROPRIATE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({
                    'type': 'inappropriate',
                    'severity': 'critical',
                    'text': name,
                    'action': 'blocked'
                })
                categories.append('inappropriate')
                severity = max(severity, 4)
                
        # Check PII
        for pattern, name in self.PII_PATTERNS:
            if re.search(pattern, text):
                issues.append({
                    'type': 'pii',
                    'severity': 'high',
                    'text': name,
                    'action': 'redacted'
                })
                categories.append('pii')
                severity = max(severity, 3)
                
        # Check AI identity
        for pattern, name in self.AI_IDENTITY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                issues.append({
                    'type': 'ai_identity',
                    'severity': 'medium',
                    'text': name,
                    'action': 'warning'
                })
                categories.append('ai_identity')
                severity = max(severity, 2)
        
        # Determine outcomes
        critical_or_high = any(
            i['severity'] in ['critical', 'high'] 
            for i in issues
        )
        
        approved = not critical_or_high
        requires_review = len(issues) > 0 and not approved
        
        # Sanitise
        sanitised = self._sanitise(text, issues)
        
        # Confidence
        confidence = min(0.99, 0.5 + (0.1 * len(issues)))
        
        return OutputScanResult(
            approved=approved,
            requires_review=requires_review,
            issues=issues,
            sanitised=sanitised,
            categories_triggered=categories,
            confidence=confidence
        )
    
    def _sanitise(self, text: str, issues: List[Dict]) -> str:
        """Remove or redact problematic content"""
        sanitised = text
        
        # Redact PII
        for pattern, _ in self.PII_PATTERNS:
            sanitised = re.sub(pattern, '[[REDACTED]]', sanitised)
            
        # Redact commitments
        for pattern, _ in self.COMMITMENT_PATTERNS:
            sanitised = re.sub(pattern, '[COMMITMENT REMOVED]', sanitised, flags=re.IGNORECASE)
            
        return sanitised

# CLI interface
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: prompt-guard-output.py <text-to-scan>")
        sys.exit(1)
        
    text = ' '.join(sys.argv[1:])
    guard = PromptGuardOutput()
    result = guard.scan(text)
    
    print(json.dumps(result.to_dict(), indent=2))
