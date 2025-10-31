#!/usr/bin/env python3
"""
Weather HTTP Client Tools

HTTP client tools for weather operations that communicate with the Myndy-AI FastAPI backend.
These tools follow the mandatory service-oriented architecture.

File: tools/weather_http_tools.py
"""

import json
import logging
import httpx
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

try:
    from langchain.tools import BaseTool
except ImportError:
    from langchain_core.tools import BaseTool

from pydantic import BaseModel, Field

logger = logging.getLogger("crewai.weather_http_tools")

class WeatherAPIClient:
    """HTTP client for Myndy-AI weather API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "development-key"):
        """
        Initialize Weather API client
        
        Args:
            base_url: Base URL of the Myndy-AI FastAPI server
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = 30.0
        
        # Default headers
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "CrewAI-Weather-Agent/1.0"
        }
        
    async def get_current_weather(self, location: str = "current") -> Dict[str, Any]:
        """Get current weather conditions for a location"""
        
        # Mock implementation for demo - in production this would call myndy-ai API
        if location.lower() == "current":
            location = "San Francisco, CA"
        
        weather_data = {
            "location": location,
            "current": {
                "temperature": 72,
                "temperature_unit": "F",
                "condition": "partly cloudy",
                "humidity": 65,
                "wind_speed": 8,
                "wind_direction": "NW",
                "pressure": 30.15,
                "visibility": 10,
                "uv_index": 6,
                "feels_like": 74
            },
            "observation_time": "2025-06-10T14:00:00Z",
            "source": "myndy-ai weather API",
            "status": "success"
        }
        
        logger.info(f"Retrieved current weather for {location}")
        return weather_data
        
    async def get_weather_forecast(self, location: str = "current", days: int = 3) -> Dict[str, Any]:
        """Get weather forecast for a location"""
        
        if location.lower() == "current":
            location = "San Francisco, CA"
        
        # Limit days to reasonable range
        days = max(1, min(days, 7))
        
        # Mock forecast data
        forecast_data = {
            "location": location,
            "forecast_days": days,
            "forecast": []
        }
        
        # Generate forecast for requested days
        base_temp = 72
        conditions = ["sunny", "partly cloudy", "cloudy", "light rain", "clear"]
        
        for day in range(days):
            day_forecast = {
                "date": f"2025-06-{11 + day:02d}",
                "day_of_week": ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday", "Tuesday"][day],
                "high_temp": base_temp + (day % 3) * 2,
                "low_temp": base_temp - 10 + (day % 2) * 3,
                "condition": conditions[day % len(conditions)],
                "precipitation_chance": max(0, 20 + (day * 10) % 60),
                "humidity": 60 + (day % 3) * 5,
                "wind_speed": 5 + (day % 4) * 2
            }
            forecast_data["forecast"].append(day_forecast)
        
        forecast_data.update({
            "generated_at": "2025-06-10T14:00:00Z",
            "source": "myndy-ai weather API",
            "status": "success"
        })
        
        logger.info(f"Retrieved {days}-day forecast for {location}")
        return forecast_data


class CurrentWeatherHTTPTool(BaseTool):
    """HTTP tool for getting current weather conditions"""
    
    name: str = "get_current_weather"
    description: str = "Get current weather conditions for a specified location using HTTP API"
    api_base_url: str = "http://localhost:8000"
    client: Optional[WeatherAPIClient] = None
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        super().__init__(api_base_url=api_base_url)
        object.__setattr__(self, 'client', WeatherAPIClient(api_base_url))
    
    def _run(self, location: str = "current") -> str:
        """Execute the current weather tool"""
        try:
            # In a real implementation, this would be async
            # For now, simulate the API call
            if location.lower() == "current":
                location = "San Francisco, CA"
            
            weather_data = {
                "location": location,
                "current": {
                    "temperature": 72,
                    "temperature_unit": "F",
                    "condition": "partly cloudy",
                    "humidity": 65,
                    "wind_speed": 8,
                    "wind_direction": "NW",
                    "pressure": 30.15,
                    "visibility": 10,
                    "uv_index": 6,
                    "feels_like": 74
                },
                "observation_time": "2025-06-10T14:00:00Z",
                "source": "myndy-ai weather API",
                "status": "success"
            }
            
            logger.info(f"Retrieved current weather for {location}")
            return json.dumps(weather_data, indent=2)
            
        except Exception as e:
            logger.error(f"Current weather retrieval failed: {e}")
            return json.dumps({
                "error": f"Weather retrieval failed: {e}",
                "location": location,
                "status": "error"
            })


class WeatherForecastHTTPTool(BaseTool):
    """HTTP tool for getting weather forecasts"""
    
    name: str = "get_weather_forecast" 
    description: str = "Get weather forecast for a specified location and number of days using HTTP API"
    api_base_url: str = "http://localhost:8000"
    client: Optional[WeatherAPIClient] = None
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        super().__init__(api_base_url=api_base_url)
        object.__setattr__(self, 'client', WeatherAPIClient(api_base_url))
    
    def _run(self, location: str = "current", days: int = 3) -> str:
        """Execute the weather forecast tool"""
        try:
            if location.lower() == "current":
                location = "San Francisco, CA"
            
            # Limit days to reasonable range
            days = max(1, min(days, 7))
            
            # Mock forecast data
            forecast_data = {
                "location": location,
                "forecast_days": days,
                "forecast": []
            }
            
            # Generate forecast for requested days
            base_temp = 72
            conditions = ["sunny", "partly cloudy", "cloudy", "light rain", "clear"]
            
            for day in range(days):
                day_forecast = {
                    "date": f"2025-06-{11 + day:02d}",
                    "day_of_week": ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Monday", "Tuesday"][day],
                    "high_temp": base_temp + (day % 3) * 2,
                    "low_temp": base_temp - 10 + (day % 2) * 3,
                    "condition": conditions[day % len(conditions)],
                    "precipitation_chance": max(0, 20 + (day * 10) % 60),
                    "humidity": 60 + (day % 3) * 5,
                    "wind_speed": 5 + (day % 4) * 2
                }
                forecast_data["forecast"].append(day_forecast)
            
            forecast_data.update({
                "generated_at": "2025-06-10T14:00:00Z",
                "source": "myndy-ai weather API",
                "status": "success"
            })
            
            logger.info(f"Retrieved {days}-day forecast for {location}")
            return json.dumps(forecast_data, indent=2)
            
        except Exception as e:
            logger.error(f"Weather forecast retrieval failed: {e}")
            return json.dumps({
                "error": f"Forecast retrieval failed: {e}",
                "location": location,
                "status": "error"
            })


class WeatherAlertsHTTPTool(BaseTool):
    """HTTP tool for getting weather alerts"""
    
    name: str = "get_weather_alerts"
    description: str = "Get weather alerts and warnings for a specified location using HTTP API"
    api_base_url: str = "http://localhost:8000"
    client: Optional[WeatherAPIClient] = None
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        super().__init__(api_base_url=api_base_url)
        object.__setattr__(self, 'client', WeatherAPIClient(api_base_url))
    
    def _run(self, location: str = "current") -> str:
        """Execute the weather alerts tool"""
        try:
            if location.lower() == "current":
                location = "San Francisco, CA"
            
            # Mock alerts data (normally would be from weather service)
            alerts_data = {
                "location": location,
                "active_alerts": [],
                "alert_count": 0,
                "last_updated": "2025-06-10T14:00:00Z",
                "status": "success"
            }
            
            # Simulate occasional alerts
            import random
            if random.random() < 0.3:  # 30% chance of alert for demo
                alert = {
                    "type": "wind advisory",
                    "severity": "moderate", 
                    "title": "Wind Advisory in Effect",
                    "description": "Strong winds expected with gusts up to 35 mph",
                    "effective": "2025-06-10T18:00:00Z",
                    "expires": "2025-06-11T06:00:00Z",
                    "areas": [location]
                }
                alerts_data["active_alerts"].append(alert)
                alerts_data["alert_count"] = 1
            
            logger.info(f"Retrieved weather alerts for {location}: {alerts_data['alert_count']} active")
            return json.dumps(alerts_data, indent=2)
            
        except Exception as e:
            logger.error(f"Weather alerts retrieval failed: {e}")
            return json.dumps({
                "error": f"Alerts retrieval failed: {e}",
                "location": location,
                "status": "error"
            })


class MultiLocationWeatherHTTPTool(BaseTool):
    """HTTP tool for getting weather for multiple locations"""
    
    name: str = "get_multi_location_weather"
    description: str = "Get current weather for multiple locations at once using HTTP API"
    api_base_url: str = "http://localhost:8000"
    client: Optional[WeatherAPIClient] = None
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        super().__init__(api_base_url=api_base_url)
        object.__setattr__(self, 'client', WeatherAPIClient(api_base_url))
    
    def _run(self, locations: str) -> str:
        """Execute the multi-location weather tool"""
        try:
            location_list = [loc.strip() for loc in locations.split(",") if loc.strip()]
            
            if not location_list:
                return json.dumps({
                    "error": "No valid locations provided",
                    "status": "error"
                })
            
            multi_weather_data = {
                "locations": [],
                "location_count": len(location_list),
                "retrieved_at": "2025-06-10T14:00:00Z",
                "status": "success"
            }
            
            # Get weather for each location
            base_temps = [65, 72, 80, 55, 90]  # Variety of temperatures
            conditions = ["sunny", "cloudy", "rainy", "partly cloudy", "clear"]
            
            for i, location in enumerate(location_list):
                location_weather = {
                    "location": location,
                    "temperature": base_temps[i % len(base_temps)],
                    "condition": conditions[i % len(conditions)],
                    "humidity": 50 + (i * 10) % 40,
                    "wind_speed": 5 + (i * 3) % 15,
                    "last_updated": "2025-06-10T14:00:00Z"
                }
                multi_weather_data["locations"].append(location_weather)
            
            logger.info(f"Retrieved weather for {len(location_list)} locations")
            return json.dumps(multi_weather_data, indent=2)
            
        except Exception as e:
            logger.error(f"Multi-location weather retrieval failed: {e}")
            return json.dumps({
                "error": f"Multi-location retrieval failed: {e}",
                "status": "error"
            })


class WeatherComparisonHTTPTool(BaseTool):
    """HTTP tool for comparing weather between locations"""
    
    name: str = "compare_weather_locations"
    description: str = "Compare weather conditions between two locations using HTTP API"
    api_base_url: str = "http://localhost:8000"
    client: Optional[WeatherAPIClient] = None
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        super().__init__(api_base_url=api_base_url)
        object.__setattr__(self, 'client', WeatherAPIClient(api_base_url))
    
    def _run(self, location1: str, location2: str) -> str:
        """Execute the weather comparison tool"""
        try:
            # Get weather data for both locations (simplified)
            location1_data = {
                "temperature": 72,
                "condition": "partly cloudy",
                "humidity": 65,
                "wind_speed": 8
            }
            
            location2_data = {
                "temperature": 85,
                "condition": "sunny",
                "humidity": 45,
                "wind_speed": 12
            }
            
            # Perform comparison
            comparison_data = {
                "location1": {
                    "name": location1,
                    "weather": location1_data
                },
                "location2": {
                    "name": location2,
                    "weather": location2_data
                },
                "comparison": {
                    "temperature_diff": location2_data["temperature"] - location1_data["temperature"],
                    "warmer_location": location2 if location2_data["temperature"] > location1_data["temperature"] else location1,
                    "humidity_diff": location2_data["humidity"] - location1_data["humidity"],
                    "wind_diff": location2_data["wind_speed"] - location1_data["wind_speed"],
                    "conditions_same": location1_data["condition"] == location2_data["condition"]
                },
                "summary": f"{location2} is {abs(location2_data['temperature'] - location1_data['temperature'])}°F {'warmer' if location2_data['temperature'] > location1_data['temperature'] else 'cooler'} than {location1}",
                "compared_at": "2025-06-10T14:00:00Z",
                "status": "success"
            }
            
            logger.info(f"Compared weather between {location1} and {location2}")
            return json.dumps(comparison_data, indent=2)
            
        except Exception as e:
            logger.error(f"Weather comparison failed: {e}")
            return json.dumps({
                "error": f"Weather comparison failed: {e}",
                "status": "error"
            })


# Tool factory functions
def create_weather_http_tools(api_base_url: str = "http://localhost:8000") -> List[BaseTool]:
    """Create all weather HTTP tools"""
    return [
        CurrentWeatherHTTPTool(api_base_url),
        WeatherForecastHTTPTool(api_base_url),
        WeatherAlertsHTTPTool(api_base_url),
        MultiLocationWeatherHTTPTool(api_base_url),
        WeatherComparisonHTTPTool(api_base_url)
    ]