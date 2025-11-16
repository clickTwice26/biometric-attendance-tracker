"""
Timezone Configuration Information

The system has been updated to use Asia/Dhaka timezone throughout.
All timestamps will now be stored and displayed in Bangladesh Standard Time (BST).

Changes made:
1. All datetime operations now use Asia/Dhaka timezone
2. Database timestamps stored in Dhaka time
3. UI displays times with "BDT" indicator
4. API responses include Dhaka timezone timestamps

No database migration needed as all timestamps are stored as naive datetime
and interpreted as Asia/Dhaka time.
"""

from app import create_app
from app.utils.timezone import now, DHAKA_TZ

def show_timezone_info():
    app = create_app()
    with app.app_context():
        current_time = now()
        print("=" * 60)
        print("TIMEZONE CONFIGURATION")
        print("=" * 60)
        print(f"✓ System configured for: Asia/Dhaka (Bangladesh)")
        print(f"✓ Current time: {current_time.strftime('%B %d, %Y %I:%M:%S %p %Z')}")
        print(f"✓ Timezone offset: UTC+6:00")
        print()
        print("All timestamps in the system now use Bangladesh Standard Time.")
        print("=" * 60)

if __name__ == '__main__':
    show_timezone_info()
