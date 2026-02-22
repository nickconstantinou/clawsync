"""
Streaming Interceptor for Prompt Guard
Scans output in chunks without blocking token stream
"""

import asyncio
import re
import json
from typing import AsyncGenerator, Callable, Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import lru_cache
import hashlib


# ============================================================================
# CACHING LAYER
# ============================================================================

class ScanCache:
    """LRU cache for input scans"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, float] = {}
        self.max_size = max_size
        self.ttl = ttl_seconds
        self._hits = 0
        self._misses = 0
    
    def _make_key(self, text: str) -> str:
        """Create cache key from text"""
        return hashlib.sha256(text.lower().strip().encode()).hexdigest()[:16]
    
    def get(self, text: str) -> Optional[Dict[str, Any]]:
        """Get cached result"""
        key = self._make_key(text)
        now = datetime.now().timestamp()
        
        if key in self._cache:
            # Check TTL
            if now - self._timestamps.get(key, 0) < self.ttl:
                self._hits += 1
                return self._cache[key]
            else:
                # Expired
                del self._cache[key]
                del self._timestamps[key]
        
        self._misses += 1
        return None
    
    def set(self, text: str, result: Dict[str, Any]):
        """Cache result"""
        key = self._make_key(text)
        
        # Evict if full
        if len(self._cache) >= self.max_size:
            # Remove oldest
            oldest = min(self._timestamps.items(), key=lambda x: x[1])
            del self._cache[oldest[0]]
            del self._timestamps[oldest[0]]
        
        self._cache[key] = result
        self._timestamps[key] = datetime.now().timestamp()
    
    def stats(self) -> Dict[str, int]:
        """Cache statistics"""
        return {
            "hits": self._hits,
            "misses": self._misses,
            "size": len(self._cache),
            "hit_rate": self._hits / max(1, self._hits + self._misses)
        }
    
    def clear(self):
        """Clear cache"""
        self._cache.clear()
        self._timestamps.clear()


# ============================================================================
# STREAMING INTERCEPTOR
# ============================================================================

@dataclass
class StreamChunk:
    """Chunk of streamed text"""
    text: str
    is_final: bool
    blocked: bool
    risk_level: str = "low"
    issues: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []


class StreamingInterceptor:
    """
    Intercepts streaming output and scans in chunks.
    Does NOT block the stream - only flags final result.
    """
    
    def __init__(self, scanner_callback: Callable, cache: ScanCache = None):
        """
        Args:
            scanner_callback: Async function that takes text and returns scan result
            cache: Optional cache for results
        """
        self._scanner = scanner_callback
        self._cache = cache or ScanCache()
        self._buffer = ""
        self._chunk_size = 50  # chars before partial scan
        self._final_scan_interval = 10  # full scan every N chunks
        self._chunk_count = 0
        
        # Patterns that require immediate blocking
        self._critical_patterns = [
            (re.compile(r"(?i)i can give.*\d+%.*discount"), "commitment"),
            (re.compile(r"(?i)\d+% off"), "commitment"),
            (re.compile(r"[\w.-]+@[\w.-]+\.\w+"), "pii_email"),
            (re.compile(r"0?7[\d\s]{9,}"), "pii_phone"),
        ]
    
    async def intercept(
        self, 
        text_generator: AsyncGenerator[str, None]
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Wrap an async text stream and yield chunks with safety info.
        
        Usage:
            async for chunk in interceptor.intercept(agent.stream()):
                yield chunk.text  # Send to user
        """
        self._buffer = ""
        self._chunk_count = 0
        
        async for text in text_generator:
            self._buffer += text
            self._chunk_count += 1
            
            # Quick check for critical patterns in chunk
            blocked, issue = self._quick_check(text)
            
            yield StreamChunk(
                text=text,
                is_final=False,
                blocked=blocked,
                risk_level="critical" if blocked else "low",
                issues=[issue] if blocked else []
            )
        
        # Final chunk - full scan
        final_result = await self._full_scan(self._buffer)
        
        yield StreamChunk(
            text="",
            is_final=True,
            blocked=final_result.get("blocked", False),
            risk_level=final_result.get("risk", "low"),
            issues=final_result.get("issues", [])
        )
    
    def _quick_check(self, chunk: str) -> tuple[bool, Optional[str]]:
        """Quick check for critical patterns without full scan"""
        for pattern, issue_type in self._critical_patterns:
            if pattern.search(chunk):
                return True, issue_type
        return False, None
    
    async def _full_scan(self, text: str) -> Dict[str, Any]:
        """Full scan with caching"""
        # Check cache
        cached = self._cache.get(text)
        if cached:
            return cached
        
        # Run full scan
        result = await self._scanner(text)
        
        # Cache result
        self._cache.set(text, result)
        
        return result
    
    async def scan_static(self, text: str) -> Dict[str, Any]:
        """Static scan (non-streaming) with caching"""
        return await self._full_scan(text)


# ============================================================================
# DECORATORS
# ============================================================================

def cached_scan(cache: ScanCache = None):
    """Decorator for caching scan results"""
    _cache = cache or ScanCache()
    
    def decorator(func):
        async def wrapper(text: str, *args, **kwargs):
            # Check cache
            cached = _cache.get(text)
            if cached:
                return cached
            
            # Run scan
            result = await func(text, *args, **kwargs)
            
            # Cache
            _cache.set(text, result)
            
            return result
        return wrapper
    return decorator


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example():
    """Example showing how to use the streaming interceptor"""
    
    # Mock scanner (replace with real PromptGuard)
    async def mock_scanner(text: str):
        await asyncio.sleep(0.01)  # Simulate async
        return {
            "safe": "discount" not in text.lower(),
            "risk": "critical" if "discount" in text.lower() else "low",
            "blocked": "discount" in text.lower(),
            "issues": ["commitment"] if "discount" in text.lower() else []
        }
    
    # Create interceptor with cache
    cache = ScanCache(max_size=100, ttl_seconds=60)
    interceptor = StreamingInterceptor(mock_scanner, cache)
    
    # Mock streaming generator
    async def mock_stream():
        words = ["Hello", "!", " I", " can", " give", " you", " 30%", " discount", " today", "!"]
        for word in words:
            await asyncio.sleep(0.01)
            yield word
    
    # Intercept the stream
    print("Streaming with interceptor:")
    async for chunk in interceptor.intercept(mock_stream()):
        if chunk.text:
            print(f"  {chunk.text}", end="", flush=True)
        if chunk.is_final:
            print(f"\n\nFinal verdict:")
            print(f"  Blocked: {chunk.blocked}")
            print(f"  Risk: {chunk.risk_level}")
            print(f"  Issues: {chunk.issues}")
    
    # Print cache stats
    print(f"\nCache stats: {cache.stats()}")


if __name__ == "__main__":
    asyncio.run(example())
