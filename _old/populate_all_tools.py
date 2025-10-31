"""
Populate All Tools in Myndy Registry

This script combines both tool repository population and monitoring tools registration
to ensure all tools are available in the myndy registry.

File: populate_all_tools.py
"""

import sys
import logging
from pathlib import Path

# Execute both population scripts
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("🔧 Step 1: Populating registry with tool repository tools...")
    exec(open("/Users/jeremy/crewAI/populate_registry.py").read())
    
    print("\n🔧 Step 2: Registering monitoring tools...")
    exec(open("/Users/jeremy/crewAI/register_monitoring_tools.py").read())
    
    print("\n✅ All tools population complete!")