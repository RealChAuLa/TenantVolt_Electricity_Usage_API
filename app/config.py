import os
from dotenv import load_dotenv
from datetime import datetime
import pytz

# Load environment variables from .env file
load_dotenv()

# Firebase configuration
FIREBASE_URL = os.getenv("FIREBASE_URL")
if not FIREBASE_URL:
    raise ValueError("FIREBASE_URL environment variable is not set. This is required for Firebase operations.")

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
if not FIREBASE_API_KEY:
    raise ValueError("FIREBASE_API_KEY environment variable is not set. This is required for Firebase operations.")

import pytz
from datetime import datetime, timedelta
import threading

# Timezone configuration
SRI_LANKA_TZ = pytz.timezone('Asia/Colombo')


# Debug time configuration
class DebugTimeTracker:
    """Class to manage debug time with automatic progression"""

    def __init__(self):
        self._debug_start_time = None
        self._start_real_time = None
        self._lock = threading.Lock()

    def set_debug_time(self, time_str):
        """Set the debug start time"""
        with self._lock:
            if time_str:
                naive_dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                self._debug_start_time = SRI_LANKA_TZ.localize(naive_dt)
                self._start_real_time = datetime.now(SRI_LANKA_TZ)
            else:
                self._debug_start_time = None
                self._start_real_time = None

    def get_current_debug_time(self):
        """Get progressing debug time based on elapsed real time"""
        with self._lock:
            if not self._debug_start_time or not self._start_real_time:
                return None

            # Calculate elapsed time since we started using debug time
            elapsed = datetime.now(SRI_LANKA_TZ) - self._start_real_time

            # Apply that elapsed time to the debug start time
            return self._debug_start_time + elapsed

    def is_enabled(self):
        """Check if debug time is enabled"""
        return self._debug_start_time is not None


# Create a global instance of the debug time tracker
debug_time_tracker = DebugTimeTracker()

# Initial debug time (set to None to use current time)
# Example format: "2025-03-01 00:00:00"

#DEBUG_START_TIME = "2025-03-01 00:00:00"
DEBUG_START_TIME = None

# Initialize the debug time tracker with the initial value
debug_time_tracker.set_debug_time(DEBUG_START_TIME)


def get_current_time():
    """
    Get current time in Sri Lanka timezone, or progressive debug time if set.

    If debug time is enabled, the time will advance naturally based on
    the elapsed real time since debug time was set.
    """
    debug_time = debug_time_tracker.get_current_debug_time()
    if debug_time:
        return debug_time
    return datetime.now(SRI_LANKA_TZ)


def set_debug_time(time_str):
    """
    Set the debug time. Pass None to disable debug time and use real time.
    Format: "YYYY-MM-DD HH:MM:SS"
    """
    debug_time_tracker.set_debug_time(time_str)


def is_debug_time_enabled():
    """Check if debug time mode is enabled"""
    return debug_time_tracker.is_enabled()