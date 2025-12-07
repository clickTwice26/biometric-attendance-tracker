# Class Attendance Report Feature

## Overview
The Class Attendance Report provides a comprehensive view of student attendance with automatic mark calculation based on attendance percentage.

## Features

### 1. **Attendance Statistics**
- **Classes Attended**: Number of completed classes (entry + exit recorded)
- **Attendance Percentage**: (Classes Attended / Total Classes) × 100
- **Average Duration**: Average time spent in class (in minutes)
- **Status**: Excellent (≥75%), Average (≥50%), Poor (<50%)

### 2. **Mark Calculation**
- **Configurable Maximum Marks**: Set the maximum marks for 100% attendance (default: 10)
- **Proportional Calculation**: Student Marks = (Attendance % / 100) × Maximum Marks
- **Dynamic Recalculation**: Change max marks to instantly recalculate all student marks

### 3. **Visual Indicators**
- **Progress Bars**: Color-coded based on attendance percentage
  - Green: ≥75% (Excellent)
  - Yellow: 50-74% (Average)
  - Red: <50% (Poor)
- **Status Badges**: Quick visual status for each student

### 4. **Export Options**
- **Print Report**: Print-friendly format
- **Export CSV**: Download attendance data as CSV file

## Access Points

### From Classes List
1. Navigate to **Classes**
2. Click the **chart icon** (📊) next to any class
3. View detailed attendance report

### Direct URL
```
http://10.217.44.113:8888/reports/class/{class_id}
```

## Mark Calculation Examples

### Example 1: Maximum Marks = 10
- Student A: 90% attendance → 9.00 marks
- Student B: 75% attendance → 7.50 marks
- Student C: 50% attendance → 5.00 marks
- Student D: 30% attendance → 3.00 marks

### Example 2: Maximum Marks = 20
- Student A: 90% attendance → 18.00 marks
- Student B: 75% attendance → 15.00 marks
- Student C: 50% attendance → 10.00 marks
- Student D: 30% attendance → 6.00 marks

## Requirements

### For Accurate Reports
1. **Set Total Classes**: Edit class to set start date, end date, and weekly schedule
2. **Complete Attendance**: Ensure students scan both entry AND exit (exit_time must be recorded)
3. **Regular Updates**: Attendance records should be up-to-date

### Counted vs Not Counted
**Counted as Attended:**
- ✅ Has both entry_time AND exit_time
- ✅ duration_minutes is calculated

**NOT Counted:**
- ❌ Only entry_time (no exit_time)
- ❌ Student didn't scan exit

## Report Sections

### 1. Header
- Class name, code, and teacher
- Quick link to class settings

### 2. Statistics Cards
- **Total Students**: Number of enrolled students
- **Total Classes**: From class configuration
- **Avg Duration**: Average class duration across all students
- **Class Average**: Average attendance percentage

### 3. Mark Configuration
- Input field to set maximum marks
- Recalculate button to update all marks
- Formula explanation

### 4. Attendance Table
Columns:
- Student Name & ID
- Classes Attended (X / Total)
- Average Duration
- Attendance % (with progress bar)
- Marks (X / Max)
- Status Badge

### 5. Export Options
- Print Report
- Export CSV

## Usage Workflow

### For Teachers
1. **Setup Class**
   - Set start date and end date
   - Configure weekly schedule
   - System calculates total classes automatically

2. **Monitor Attendance**
   - Students scan fingerprint at entry and exit
   - System tracks entry/exit times and duration

3. **Generate Report**
   - Go to Classes → Click report icon
   - Set maximum marks (e.g., 10 for grading)
   - View individual student performance

4. **Export Data**
   - Print for physical records
   - Export CSV for Excel/Sheets processing
   - Share with administration

### For Students
- Scan fingerprint at **entry** when class starts
- Scan fingerprint at **exit** when leaving
- Both scans required for attendance to count
- 3-minute cooldown between entry and exit

## Grading Scale Recommendations

### Conservative (Strict)
- 95-100%: A+ (Full marks)
- 90-94%: A
- 85-89%: A-
- 80-84%: B+
- Below 75%: Failing

### Moderate (Balanced)
- 90-100%: A+ (Full marks)
- 80-89%: A
- 70-79%: B
- 60-69%: C
- Below 60%: Failing

### Lenient (Flexible)
- 85-100%: A+ (Full marks)
- 75-84%: A
- 65-74%: B
- 55-64%: C
- Below 55%: Failing

## Technical Details

### Database Queries
- Fetches all students in class
- Counts attendance with `exit_time IS NOT NULL`
- Calculates average from `duration_minutes`
- Real-time calculation (no caching)

### Performance
- Optimized for classes up to 200 students
- Instant mark recalculation
- Efficient database queries with proper indexing

### Future Enhancements
- Weighted marks (late entry penalty)
- Minimum duration requirements
- Attendance trend graphs
- Email reports to students
- Bulk PDF export
- Grade distribution charts
- Attendance forecasting
