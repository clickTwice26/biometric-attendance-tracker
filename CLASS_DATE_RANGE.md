# Class Date Range and Total Classes Calculation

## Overview
Each class now tracks a start date and end date for the course duration. The system automatically calculates the total number of available classes based on:
- Course start date
- Course end date  
- Weekly schedule (which days the class meets)

## Features

### 1. Start Date & End Date Fields
- **Start Date**: When the course begins
- **End Date**: When the course ends
- Both fields are optional but recommended for accurate tracking

### 2. Automatic Calculation
The system automatically calculates total available classes by:
1. Counting all dates between start and end date
2. Filtering only the days when class is scheduled (e.g., Monday, Wednesday, Friday)
3. Displaying the result in real-time as you configure the schedule

### 3. Real-Time Display
- As you select days in the weekly schedule, the total updates automatically
- As you change start/end dates, the total recalculates
- Visual indicator shows the calculated total classes

## Usage

### Adding a New Class
1. Navigate to **Classes** > **Add New Class**
2. Fill in basic information (name, code, teacher)
3. Set **Start Date** and **End Date**
4. Configure **Weekly Schedule** by:
   - Checking boxes for days the class meets
   - Setting start and end times for each day
5. Watch the **Total Available Classes** counter update automatically
6. Click **Save Class**

### Editing an Existing Class
1. Navigate to **Classes** > Select a class > **Edit**
2. Modify **Start Date** or **End Date** if needed
3. Update **Weekly Schedule** as needed
4. The **Total Available Classes** recalculates automatically
5. Click **Update Class**

## Example Calculation

**Scenario:**
- Start Date: January 1, 2025
- End Date: April 30, 2025 (120 days)
- Schedule: Monday, Wednesday, Friday

**Calculation:**
- Total days in range: 120
- Days that fall on Mon/Wed/Fri: ~52 classes
- Result: **52 Total Available Classes**

## Database Schema

### New Fields in `classes` Table
```sql
start_date DATE NULL          -- Course start date
end_date DATE NULL            -- Course end date  
total_classes INTEGER NULL    -- Calculated total available classes
```

## Benefits

1. **Attendance Tracking**: Know exactly how many classes are scheduled
2. **Attendance Rate**: Calculate student attendance percentage (attended / total_classes)
3. **Planning**: Better course planning and scheduling
4. **Reporting**: Generate accurate attendance reports based on total available classes

## Future Enhancements

Potential features to add:
- Attendance percentage calculation per student
- Alerts when students fall below attendance threshold
- Holiday/skip date management (exclude specific dates)
- Mid-semester schedule changes
- Automatic end date suggestion based on number of weeks

## Technical Details

### Frontend Calculation (JavaScript)
```javascript
function calculateTotalClasses() {
    // Get date range
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    // Get enabled days (0=Sunday, 1=Monday, etc.)
    const enabledDays = getEnabledDays();
    
    // Count matching days
    let totalClasses = 0;
    const currentDate = new Date(start);
    
    while (currentDate <= end) {
        if (enabledDays.includes(currentDate.getDay())) {
            totalClasses++;
        }
        currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return totalClasses;
}
```

### Backend Storage
- Dates stored in `YYYY-MM-DD` format (ISO 8601)
- Total classes stored as integer
- All dates stored in Asia/Dhaka timezone context

## Migration

Run the migration script to add new fields:
```bash
python3 migrate_class_dates.py
```

This adds:
- `start_date` column (DATE, nullable)
- `end_date` column (DATE, nullable)
- `total_classes` column (INTEGER, nullable)

Existing classes will have NULL values until updated through the edit page.
