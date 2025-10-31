#!/usr/bin/env python3
"""
Enhanced logging configuration for Myndy AI Pipeline
"""

import logging
import sys
from datetime import datetime

def setup_enhanced_logging():
    """Setup enhanced logging with timestamps and colors"""
    
    # Create custom formatter
    class ColoredFormatter(logging.Formatter):
        """Custom formatter with colors and emojis"""
        
        COLORS = {
            'DEBUG': '\033[36m',     # Cyan
            'INFO': '\033[32m',      # Green
            'WARNING': '\033[33m',   # Yellow
            'ERROR': '\033[31m',     # Red
            'CRITICAL': '\033[35m',  # Magenta
        }
        
        RESET = '\033[0m'
        
        EMOJIS = {
            'DEBUG': '🔍',
            'INFO': '📋',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨',
        }
        
        def format(self, record):
            # Add timestamp
            record.timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Add color and emoji
            color = self.COLORS.get(record.levelname, '')
            emoji = self.EMOJIS.get(record.levelname, '📋')
            reset = self.RESET
            
            # Format message
            log_message = f"{color}{emoji} [{record.timestamp}] {record.levelname:8} {record.name:20} | {record.getMessage()}{reset}"
            
            return log_message
    
    # Setup root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColoredFormatter())
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Also setup uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)
    
    return logger

if __name__ == "__main__":
    # Test the logging
    logger = setup_enhanced_logging()
    logger.info("🚀 Enhanced logging system initialized")
    logger.debug("🔍 Debug message example")
    logger.warning("⚠️ Warning message example")
    logger.error("❌ Error message example")