"""
Timezone utility for Asia/Dhaka timezone
"""
from datetime import datetime
import pytz

# Define Dhaka timezone
DHAKA_TZ = pytz.timezone('Asia/Dhaka')

def now():
    """Get current datetime in Asia/Dhaka timezone"""
    return datetime.now(DHAKA_TZ)

def utc_to_dhaka(utc_dt):
    """Convert UTC datetime to Dhaka timezone"""
    if utc_dt is None:
        return None
    if utc_dt.tzinfo is None:
        # Assume UTC if no timezone info
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(DHAKA_TZ)

def get_naive_now():
    """Get current datetime in Dhaka timezone without timezone info (for database storage)"""
    return datetime.now(DHAKA_TZ).replace(tzinfo=None)

def get_today_start():
    """Get start of today in Dhaka timezone"""
    dhaka_now = datetime.now(DHAKA_TZ)
    return dhaka_now.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

def get_today_end():
    """Get end of today in Dhaka timezone"""
    dhaka_now = datetime.now(DHAKA_TZ)
    return dhaka_now.replace(hour=23, minute=59, second=59, microsecond=999999, tzinfo=None)
