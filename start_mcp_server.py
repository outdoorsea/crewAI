#!/usr/bin/env python3
"""
Start MCP Server

Convenience script to start the Myndy CrewAI MCP server.

Usage:
    python start_mcp_server.py
"""

import sys
import asyncio

# Ensure myndy_crewai_mcp is importable
from myndy_crewai_mcp.main import main

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)
