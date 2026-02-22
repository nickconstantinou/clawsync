"""CLI entry point"""
import asyncio
import sys

from prompt_guard.stateful_guard import AdvancedGuard


async def main():
    guard = AdvancedGuard()
    
    if len(sys.argv) < 2:
        print("Usage: python -m prompt_guard <input|output|status|lock|unlock> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        print(guard.killswitch.status())
    elif cmd == "lock":
        guard.killswitch.lock(sys.argv[2] if len(sys.argv) > 2 else "cli")
        print("Locked")
    elif cmd == "unlock":
        guard.killswitch.unlock()
        print("Unlocked")
    elif cmd == "input" and len(sys.argv) > 3:
        result = await guard.check_input(sys.argv[3], sys.argv[2])
        print(result)
    elif cmd == "output" and len(sys.argv) > 3:
        result = await guard.check_output(sys.argv[3], sys.argv[2])
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
