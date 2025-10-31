"""
runtime_config.py - Runtime configuration for production vs testing modes

This module provides runtime configuration switching between production mode
(fail-fast) and testing mode (graceful degradation) for the CrewAI system.

File: config/runtime_config.py
"""

import os
import logging
from enum import Enum
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class RuntimeMode(Enum):
    """Runtime execution modes"""
    PRODUCTION = "production"
    TESTING = "testing"
    DEVELOPMENT = "development"


class RuntimeConfig:
    """Runtime configuration manager with production/testing mode switching"""
    
    def __init__(self):
        self._mode = None
        self._config_overrides = {}
        self._detect_mode()
    
    def _detect_mode(self) -> None:
        """Auto-detect runtime mode from environment"""
        # Check environment variable first
        env_mode = os.getenv('CREWAI_MODE', '').lower()
        
        if env_mode in ['production', 'prod']:
            self._mode = RuntimeMode.PRODUCTION
        elif env_mode in ['testing', 'test']:
            self._mode = RuntimeMode.TESTING
        elif env_mode in ['development', 'dev']:
            self._mode = RuntimeMode.DEVELOPMENT
        else:
            # Auto-detect based on context
            if self._is_testing_context():
                self._mode = RuntimeMode.TESTING
            elif self._is_production_context():
                self._mode = RuntimeMode.PRODUCTION
            else:
                self._mode = RuntimeMode.DEVELOPMENT
    
    def _is_testing_context(self) -> bool:
        """Detect if we're running in a testing context"""
        testing_indicators = [
            'pytest' in os.getenv('_', ''),  # pytest runner
            'pytest' in str(Path.cwd()),     # pytest directory
            os.getenv('CI') == 'true',       # CI environment
            'test' in os.getenv('PWD', ''),  # test directory
            any('pytest' in arg for arg in os.sys.argv),  # pytest in args
            any('test' in arg for arg in os.sys.argv),    # test in args
        ]
        return any(testing_indicators)
    
    def _is_production_context(self) -> bool:
        """Detect if we're running in production context"""
        production_indicators = [
            os.getenv('ENVIRONMENT') == 'production',
            os.getenv('NODE_ENV') == 'production',
            os.getenv('FLASK_ENV') == 'production',
            os.getenv('DJANGO_SETTINGS_MODULE', '').endswith('production'),
            'heroku' in os.getenv('DYNO', '').lower(),
            os.getenv('PORT') is not None,  # Often indicates deployed app
        ]
        return any(production_indicators)
    
    @property
    def mode(self) -> RuntimeMode:
        """Get current runtime mode"""
        return self._mode
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self._mode == RuntimeMode.PRODUCTION
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self._mode == RuntimeMode.TESTING
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self._mode == RuntimeMode.DEVELOPMENT
    
    def set_mode(self, mode: RuntimeMode) -> None:
        """Explicitly set runtime mode"""
        old_mode = self._mode
        self._mode = mode
        logger.info(f"Runtime mode changed: {old_mode.value} → {mode.value}")
    
    def set_mode_from_string(self, mode_str: str) -> None:
        """Set mode from string"""
        mode_str = mode_str.lower()
        mode_mapping = {
            'production': RuntimeMode.PRODUCTION,
            'prod': RuntimeMode.PRODUCTION,
            'testing': RuntimeMode.TESTING,
            'test': RuntimeMode.TESTING,
            'development': RuntimeMode.DEVELOPMENT,
            'dev': RuntimeMode.DEVELOPMENT,
        }
        
        if mode_str in mode_mapping:
            self.set_mode(mode_mapping[mode_str])
        else:
            raise ValueError(f"Invalid mode: {mode_str}. Valid modes: {list(mode_mapping.keys())}")
    
    def get_behavior_config(self) -> Dict[str, Any]:
        """Get behavior configuration based on current mode"""
        if self.is_production:
            return {
                'fail_on_missing_dependencies': True,
                'fail_on_agent_creation_error': True,
                'fail_on_api_unavailable': True,
                'allow_mock_agents': False,
                'allow_fallback_mechanisms': False,
                'error_on_missing_tools': True,
                'skip_tests_on_missing_deps': False,
                'verbose_dependency_logging': False,
                'timeout_behavior': 'fail',
                'degradation_strategy': 'fail_fast',
            }
        elif self.is_testing:
            return {
                'fail_on_missing_dependencies': False,
                'fail_on_agent_creation_error': False,
                'fail_on_api_unavailable': False,
                'allow_mock_agents': True,
                'allow_fallback_mechanisms': True,
                'error_on_missing_tools': False,
                'skip_tests_on_missing_deps': True,
                'verbose_dependency_logging': True,
                'timeout_behavior': 'skip',
                'degradation_strategy': 'graceful',
            }
        else:  # development
            return {
                'fail_on_missing_dependencies': False,
                'fail_on_agent_creation_error': False,
                'fail_on_api_unavailable': False,
                'allow_mock_agents': True,
                'allow_fallback_mechanisms': True,
                'error_on_missing_tools': False,
                'skip_tests_on_missing_deps': True,
                'verbose_dependency_logging': True,
                'timeout_behavior': 'warn',
                'degradation_strategy': 'graceful_with_warnings',
            }
    
    def override_config(self, **kwargs) -> None:
        """Override specific configuration values"""
        self._config_overrides.update(kwargs)
        logger.debug(f"Config overrides applied: {kwargs}")
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get configuration value with override support"""
        if key in self._config_overrides:
            return self._config_overrides[key]
        
        behavior_config = self.get_behavior_config()
        return behavior_config.get(key, default)
    
    def should_fail_fast(self, operation: str) -> bool:
        """Check if operation should fail fast in current mode"""
        fail_fast_operations = {
            'missing_dependencies': 'fail_on_missing_dependencies',
            'agent_creation_error': 'fail_on_agent_creation_error',
            'api_unavailable': 'fail_on_api_unavailable',
            'missing_tools': 'error_on_missing_tools',
        }
        
        config_key = fail_fast_operations.get(operation)
        if config_key:
            return self.get_config_value(config_key, False)
        
        # Default to production behavior for unknown operations
        return self.is_production
    
    def should_use_fallback(self, component: str) -> bool:
        """Check if component should use fallback mechanisms"""
        if component == 'agents':
            return self.get_config_value('allow_mock_agents', False)
        elif component == 'api':
            return self.get_config_value('allow_fallback_mechanisms', False)
        
        # Default based on mode
        return not self.is_production
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        return {
            'mode': self._mode.value,
            'is_production': self.is_production,
            'is_testing': self.is_testing,
            'is_development': self.is_development,
            'behavior_config': self.get_behavior_config(),
            'overrides': self._config_overrides,
            'detection_method': self._get_detection_method(),
        }
    
    def _get_detection_method(self) -> str:
        """Get how the mode was detected"""
        env_mode = os.getenv('CREWAI_MODE')
        if env_mode:
            return f"environment_variable: CREWAI_MODE={env_mode}"
        elif self._is_testing_context():
            return "auto_detected: testing_context"
        elif self._is_production_context():
            return "auto_detected: production_context"
        else:
            return "default: development"


# Global runtime configuration instance
runtime_config = RuntimeConfig()


def get_runtime_config() -> RuntimeConfig:
    """Get the global runtime configuration instance"""
    return runtime_config


def is_production_mode() -> bool:
    """Quick check for production mode"""
    return runtime_config.is_production


def is_testing_mode() -> bool:
    """Quick check for testing mode"""
    return runtime_config.is_testing


def should_fail_fast(operation: str = 'default') -> bool:
    """Quick check if operation should fail fast"""
    return runtime_config.should_fail_fast(operation)


def should_use_fallback(component: str = 'default') -> bool:
    """Quick check if component should use fallbacks"""
    return runtime_config.should_use_fallback(component)


def set_production_mode() -> None:
    """Switch to production mode"""
    runtime_config.set_mode(RuntimeMode.PRODUCTION)


def set_testing_mode() -> None:
    """Switch to testing mode"""
    runtime_config.set_mode(RuntimeMode.TESTING)


def print_runtime_status():
    """Print current runtime configuration status"""
    status = runtime_config.get_status_summary()
    
    print("🎯 CREWAI RUNTIME CONFIGURATION")
    print("=" * 50)
    print(f"Mode: {status['mode'].upper()}")
    print(f"Detection: {status['detection_method']}")
    
    behavior = status['behavior_config']
    print(f"\n🚀 BEHAVIOR CONFIGURATION:")
    print(f"  Fail on missing deps: {behavior['fail_on_missing_dependencies']}")
    print(f"  Fail on agent errors: {behavior['fail_on_agent_creation_error']}")
    print(f"  Allow mock agents: {behavior['allow_mock_agents']}")
    print(f"  Allow fallbacks: {behavior['allow_fallback_mechanisms']}")
    print(f"  Degradation strategy: {behavior['degradation_strategy']}")
    
    if status['overrides']:
        print(f"\n⚙️  OVERRIDES: {status['overrides']}")
    
    print("=" * 50)


if __name__ == "__main__":
    print_runtime_status()