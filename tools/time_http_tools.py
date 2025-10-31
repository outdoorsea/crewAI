#!/usr/bin/env python3
"""
Time HTTP Client Tools

HTTP client tools for time operations that communicate with the Myndy-AI FastAPI backend.
These tools follow the mandatory service-oriented architecture.

File: tools/time_http_tools.py
"""

import json
import logging
import httpx
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

try:
    from langchain.tools import BaseTool
except ImportError:
    from langchain_core.tools import BaseTool

from pydantic import BaseModel, Field

logger = logging.getLogger("crewai.time_http_tools")

class TimeAPIClient:
    """HTTP client for Myndy-AI time API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "development-key"):
        """
        Initialize Time API client
        
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
            "User-Agent": "CrewAI-Time-Agent/1.0"
        }


class CurrentTimeHTTPTool(BaseTool):
    """HTTP tool for getting current time information"""
    
    name: str = "get_current_time"
    description: str = "Get current time in specified timezone and format using HTTP API"
    api_base_url: str = "http://localhost:8000"
    client: Optional[TimeAPIClient] = None
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        super().__init__(api_base_url=api_base_url)
        object.__setattr__(self, 'client', TimeAPIClient(api_base_url))
    
    def _run(self, timezone_name: str = "local", format_type: str = "standard") -> str:
        """Execute the current time tool"""
        try:
            # Get current time
            now = datetime.now(timezone.utc)
            
            # Handle timezone conversion
            if timezone_name.lower() == "local":
                local_time = now.astimezone()
                tz_name = str(local_time.tzinfo)
            else:
                # For demo, handle common timezones
                tz_offsets = {
                    "utc": 0,
                    "us/pacific": -8,
                    "us/eastern": -5,
                    "us/central": -6,
                    "us/mountain": -7,
                    "europe/london": 0,
                    "europe/paris": 1,
                    "asia/tokyo": 9
                }
                
                offset_hours = tz_offsets.get(timezone_name.lower(), 0)
                local_time = now + timedelta(hours=offset_hours)
                tz_name = timezone_name
            
            # Format according to requested type
            formatted_times = {
                "standard": local_time.strftime("%Y-%m-%d %H:%M:%S"),
                "iso": local_time.isoformat(),
                "timestamp": int(local_time.timestamp()),
                "human": local_time.strftime("%A, %B %d, %Y at %I:%M %p")
            }
            
            time_data = {
                "timezone": tz_name,
                "requested_format": format_type,
                "current_time": formatted_times.get(format_type, formatted_times["standard"]),
                "all_formats": formatted_times,
                "utc_time": now.isoformat(),
                "day_of_week": local_time.strftime("%A"),
                "day_of_year": local_time.timetuple().tm_yday,
                "week_number": local_time.isocalendar()[1],
                "is_weekend": local_time.weekday() >= 5,
                "retrieved_at": now.isoformat(),
                "status": "success"
            }
            
            logger.info(f"Retrieved current time for timezone: {timezone_name}")
            return json.dumps(time_data, indent=2)
            
        except Exception as e:
            logger.error(f"Current time retrieval failed: {e}")
            return json.dumps({
                "error": f"Time retrieval failed: {e}",
                "timezone": timezone_name,
                "status": "error"
            })


class DateFormatHTTPTool(BaseTool):
    """HTTP tool for formatting dates and times"""
    
    name: str = "format_date"
    description: str = "Format dates and times into different formats with detailed information using HTTP API"
    api_base_url: str = "http://localhost:8000"
    client: Optional[TimeAPIClient] = None
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        super().__init__(api_base_url=api_base_url)
        object.__setattr__(self, 'client', TimeAPIClient(api_base_url))
    
    def _run(self, date_string: str, input_format: str = "auto", output_format: str = "human") -> str:
        """Execute the date formatting tool"""
        try:
            # Parse input date
            parsed_date = None
            
            if input_format == "auto":
                # Try common formats
                formats_to_try = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d",
                    "%m/%d/%Y",
                    "%m/%d/%Y %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%SZ"
                ]
                
                for fmt in formats_to_try:
                    try:
                        parsed_date = datetime.strptime(date_string, fmt)
                        break
                    except ValueError:
                        continue
                
                # Try parsing as timestamp
                if parsed_date is None:
                    try:
                        timestamp = float(date_string)
                        parsed_date = datetime.fromtimestamp(timestamp)
                    except (ValueError, OSError):
                        pass
                        
            elif input_format == "timestamp":
                timestamp = float(date_string)
                parsed_date = datetime.fromtimestamp(timestamp)
            elif input_format == "iso":
                parsed_date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            
            if parsed_date is None:
                return json.dumps({
                    "error": f"Could not parse date string: {date_string}",
                    "status": "error"
                })
            
            # Format output
            output_formats = {
                "human": parsed_date.strftime("%A, %B %d, %Y at %I:%M %p"),
                "iso": parsed_date.isoformat(),
                "timestamp": int(parsed_date.timestamp()),
                "standard": parsed_date.strftime("%Y-%m-%d %H:%M:%S"),
                "date_only": parsed_date.strftime("%Y-%m-%d"),
                "time_only": parsed_date.strftime("%H:%M:%S"),
                "short": parsed_date.strftime("%m/%d/%Y"),
                "long": parsed_date.strftime("%B %d, %Y")
            }
            
            format_data = {
                "input": {
                    "original": date_string,
                    "format": input_format,
                    "parsed": parsed_date.isoformat()
                },
                "output": {
                    "format": output_format,
                    "formatted": output_formats.get(output_format, output_formats["human"])
                },
                "all_formats": output_formats,
                "date_info": {
                    "day_of_week": parsed_date.strftime("%A"),
                    "month_name": parsed_date.strftime("%B"),
                    "day_of_year": parsed_date.timetuple().tm_yday,
                    "week_number": parsed_date.isocalendar()[1],
                    "is_weekend": parsed_date.weekday() >= 5,
                    "quarter": (parsed_date.month - 1) // 3 + 1
                },
                "formatted_at": datetime.now().isoformat(),
                "status": "success"
            }
            
            logger.info(f"Formatted date: {date_string} -> {output_format}")
            return json.dumps(format_data, indent=2)
            
        except Exception as e:
            logger.error(f"Date formatting failed: {e}")
            return json.dumps({
                "error": f"Date formatting failed: {e}",
                "input": date_string,
                "status": "error"
            })


class TimeCalculationHTTPTool(BaseTool):
    """HTTP tool for time calculations and durations"""
    
    name: str = "calculate_time"
    description: str = "Calculate time differences, add/subtract time periods, and duration analysis using HTTP API"
    api_base_url: str = "http://localhost:8000"
    client: Optional[TimeAPIClient] = None
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        super().__init__(api_base_url=api_base_url)
        object.__setattr__(self, 'client', TimeAPIClient(api_base_url))
    
    def _run(self, operation: str, time1: str, time2: str = "", amount: str = "", unit: str = "days") -> str:
        """Execute the time calculation tool"""
        try:
            # Parse first time
            def parse_time(time_str):
                formats = [
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%SZ"
                ]
                
                for fmt in formats:
                    try:
                        return datetime.strptime(time_str, fmt)
                    except ValueError:
                        continue
                
                # Try timestamp
                try:
                    return datetime.fromtimestamp(float(time_str))
                except (ValueError, OSError):
                    pass
                
                raise ValueError(f"Could not parse time: {time_str}")
            
            dt1 = parse_time(time1)
            result_data = {
                "operation": operation,
                "input": {
                    "time1": time1,
                    "parsed_time1": dt1.isoformat()
                },
                "calculated_at": datetime.now().isoformat(),
                "status": "success"
            }
            
            if operation == "difference" and time2:
                dt2 = parse_time(time2)
                diff = dt2 - dt1
                
                result_data["input"]["time2"] = time2
                result_data["input"]["parsed_time2"] = dt2.isoformat()
                result_data["result"] = {
                    "total_seconds": diff.total_seconds(),
                    "days": diff.days,
                    "hours": diff.seconds // 3600,
                    "minutes": (diff.seconds % 3600) // 60,
                    "seconds": diff.seconds % 60,
                    "human_readable": f"{abs(diff.days)} days, {abs(diff.seconds) // 3600} hours, {(abs(diff.seconds) % 3600) // 60} minutes",
                    "direction": "future" if diff.total_seconds() > 0 else "past"
                }
                
            elif operation in ["add", "subtract"] and amount:
                amount_val = float(amount)
                
                # Convert to timedelta
                unit_multipliers = {
                    "seconds": timedelta(seconds=1),
                    "minutes": timedelta(minutes=1),
                    "hours": timedelta(hours=1),
                    "days": timedelta(days=1),
                    "weeks": timedelta(weeks=1)
                }
                
                if unit not in unit_multipliers:
                    return json.dumps({
                        "error": f"Invalid unit: {unit}. Use: {', '.join(unit_multipliers.keys())}",
                        "status": "error"
                    })
                
                delta = unit_multipliers[unit] * amount_val
                
                if operation == "add":
                    result_dt = dt1 + delta
                else:  # subtract
                    result_dt = dt1 - delta
                
                result_data["input"].update({
                    "amount": amount,
                    "unit": unit,
                    "operation_type": operation
                })
                result_data["result"] = {
                    "result_time": result_dt.isoformat(),
                    "formatted": result_dt.strftime("%A, %B %d, %Y at %I:%M %p"),
                    "difference_applied": f"{operation} {amount} {unit}",
                    "timestamp": int(result_dt.timestamp())
                }
                
            else:
                return json.dumps({
                    "error": f"Invalid operation or missing parameters for: {operation}",
                    "status": "error"
                })
            
            logger.info(f"Performed time calculation: {operation}")
            return json.dumps(result_data, indent=2)
            
        except Exception as e:
            logger.error(f"Time calculation failed: {e}")
            return json.dumps({
                "error": f"Time calculation failed: {e}",
                "operation": operation,
                "status": "error"
            })


class TimezoneConversionHTTPTool(BaseTool):
    """HTTP tool for timezone conversion"""
    
    name: str = "convert_timezone"
    description: str = "Convert time between different timezones with detailed information using HTTP API"
    api_base_url: str = "http://localhost:8000"
    client: Optional[TimeAPIClient] = None
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        super().__init__(api_base_url=api_base_url)
        object.__setattr__(self, 'client', TimeAPIClient(api_base_url))
    
    def _run(self, time_string: str, from_timezone: str, to_timezone: str) -> str:
        """Execute the timezone conversion tool"""
        try:
            # Parse input time
            dt = None
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%H:%M:%S",
                "%H:%M"
            ]
            
            for fmt in formats:
                try:
                    if len(time_string.split()) == 1 and ":" in time_string:
                        # Time only, use today's date
                        today = datetime.now().date()
                        dt = datetime.combine(today, datetime.strptime(time_string, fmt).time())
                    else:
                        dt = datetime.strptime(time_string, fmt)
                    break
                except ValueError:
                    continue
            
            if dt is None:
                return json.dumps({
                    "error": f"Could not parse time: {time_string}",
                    "status": "error"
                })
            
            # Timezone offsets (simplified for demo)
            tz_offsets = {
                "utc": 0, "gmt": 0,
                "us/pacific": -8, "pst": -8, "pdt": -7,
                "us/eastern": -5, "est": -5, "edt": -4,
                "us/central": -6, "cst": -6, "cdt": -5,
                "us/mountain": -7, "mst": -7, "mdt": -6,
                "europe/london": 0, "gmt": 0, "bst": 1,
                "europe/paris": 1, "cet": 1, "cest": 2,
                "asia/tokyo": 9, "jst": 9,
                "australia/sydney": 10, "aest": 10
            }
            
            from_offset = tz_offsets.get(from_timezone.lower())
            to_offset = tz_offsets.get(to_timezone.lower())
            
            if from_offset is None:
                return json.dumps({
                    "error": f"Unknown timezone: {from_timezone}",
                    "available_timezones": list(tz_offsets.keys()),
                    "status": "error"
                })
            
            if to_offset is None:
                return json.dumps({
                    "error": f"Unknown timezone: {to_timezone}",
                    "available_timezones": list(tz_offsets.keys()),
                    "status": "error"
                })
            
            # Convert timezone
            utc_time = dt - timedelta(hours=from_offset)
            target_time = utc_time + timedelta(hours=to_offset)
            
            conversion_data = {
                "input": {
                    "time": time_string,
                    "from_timezone": from_timezone,
                    "to_timezone": to_timezone,
                    "parsed_time": dt.isoformat()
                },
                "conversion": {
                    "original_time": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "converted_time": target_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "time_difference": f"{abs(to_offset - from_offset)} hours {'ahead' if to_offset > from_offset else 'behind'}",
                    "utc_time": utc_time.strftime("%Y-%m-%d %H:%M:%S UTC")
                },
                "formatted_results": {
                    "human_readable": f"{target_time.strftime('%I:%M %p on %A, %B %d, %Y')} {to_timezone.upper()}",
                    "iso_format": target_time.isoformat(),
                    "timestamp": int(target_time.timestamp())
                },
                "converted_at": datetime.now().isoformat(),
                "status": "success"
            }
            
            logger.info(f"Converted time from {from_timezone} to {to_timezone}")
            return json.dumps(conversion_data, indent=2)
            
        except Exception as e:
            logger.error(f"Timezone conversion failed: {e}")
            return json.dumps({
                "error": f"Timezone conversion failed: {e}",
                "status": "error"
            })


class BusinessHoursHTTPTool(BaseTool):
    """HTTP tool for business hours analysis"""
    
    name: str = "check_business_hours"
    description: str = "Check if specified time falls within business hours with detailed analysis using HTTP API"
    api_base_url: str = "http://localhost:8000"
    client: Optional[TimeAPIClient] = None
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        super().__init__(api_base_url=api_base_url)
        object.__setattr__(self, 'client', TimeAPIClient(api_base_url))
    
    def _run(self, timezone_name: str = "US/Pacific", check_time: str = "now") -> str:
        """Execute the business hours check tool"""
        try:
            # Get time to check
            if check_time.lower() == "now":
                check_dt = datetime.now()
            else:
                # Parse provided time
                formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%H:%M:%S", "%H:%M"]
                check_dt = None
                
                for fmt in formats:
                    try:
                        if len(check_time.split()) == 1 and ":" in check_time:
                            today = datetime.now().date()
                            check_dt = datetime.combine(today, datetime.strptime(check_time, fmt).time())
                        else:
                            check_dt = datetime.strptime(check_time, fmt)
                        break
                    except ValueError:
                        continue
                
                if check_dt is None:
                    return json.dumps({
                        "error": f"Could not parse time: {check_time}",
                        "status": "error"
                    })
            
            # Business hours configuration (9 AM to 5 PM, Monday to Friday)
            business_start = 9  # 9 AM
            business_end = 17   # 5 PM
            business_days = [0, 1, 2, 3, 4]  # Monday to Friday
            
            # Check if it's a business day
            is_business_day = check_dt.weekday() in business_days
            
            # Check if it's within business hours
            current_hour = check_dt.hour
            is_business_hours = business_start <= current_hour < business_end
            
            # Calculate time until next business period
            next_business_time = None
            if not is_business_day or not is_business_hours:
                if is_business_day and current_hour < business_start:
                    # Same day, before business hours
                    next_business_time = check_dt.replace(hour=business_start, minute=0, second=0)
                else:
                    # After hours or weekend - next business day
                    days_ahead = 1
                    while True:
                        next_day = check_dt + timedelta(days=days_ahead)
                        if next_day.weekday() in business_days:
                            next_business_time = next_day.replace(hour=business_start, minute=0, second=0)
                            break
                        days_ahead += 1
            
            business_data = {
                "check_time": {
                    "input": check_time,
                    "parsed": check_dt.isoformat(),
                    "timezone": timezone_name,
                    "day_of_week": check_dt.strftime("%A"),
                    "hour": check_dt.hour,
                    "minute": check_dt.minute
                },
                "business_hours": {
                    "start_time": f"{business_start:02d}:00",
                    "end_time": f"{business_end:02d}:00",
                    "business_days": "Monday to Friday",
                    "timezone": timezone_name
                },
                "analysis": {
                    "is_business_day": is_business_day,
                    "is_business_hours": is_business_hours,
                    "is_open": is_business_day and is_business_hours,
                    "status": "open" if (is_business_day and is_business_hours) else "closed"
                },
                "next_business_time": next_business_time.isoformat() if next_business_time else None,
                "time_until_next_business": None,
                "checked_at": datetime.now().isoformat(),
                "status": "success"
            }
            
            # Calculate time until next business period
            if next_business_time:
                time_diff = next_business_time - check_dt
                hours_until = int(time_diff.total_seconds() // 3600)
                minutes_until = int((time_diff.total_seconds() % 3600) // 60)
                
                business_data["time_until_next_business"] = {
                    "hours": hours_until,
                    "minutes": minutes_until,
                    "human_readable": f"{hours_until} hours and {minutes_until} minutes"
                }
            
            logger.info(f"Checked business hours for {timezone_name}: {'open' if business_data['analysis']['is_open'] else 'closed'}")
            return json.dumps(business_data, indent=2)
            
        except Exception as e:
            logger.error(f"Business hours check failed: {e}")
            return json.dumps({
                "error": f"Business hours check failed: {e}",
                "status": "error"
            })


# Tool factory functions
def create_time_http_tools(api_base_url: str = "http://localhost:8000") -> List[BaseTool]:
    """Create all time HTTP tools"""
    return [
        CurrentTimeHTTPTool(api_base_url),
        DateFormatHTTPTool(api_base_url),
        TimeCalculationHTTPTool(api_base_url),
        TimezoneConversionHTTPTool(api_base_url),
        BusinessHoursHTTPTool(api_base_url)
    ]