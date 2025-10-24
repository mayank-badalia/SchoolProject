import sqlite3
from datetime import datetime

class AttendanceSystem:
    def __init__(self):
        """Initialize database connection"""
        self.conn = sqlite3.connect('attendance.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        """Create necessary tables"""
        # Students table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY,
                roll_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                class TEXT NOT NULL,
                section TEXT NOT NULL
            )
        """)
        
        # Attendance table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id INTEGER PRIMARY KEY,
                roll_no TEXT NOT NULL,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                reason TEXT,
                FOREIGN KEY (roll_no) REFERENCES students(roll_no) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
    
    def get_next_student_id(self):
        """Get next available student ID (fills gaps)"""
        self.cursor.execute("SELECT student_id FROM students ORDER BY student_id")
        ids = [row[0] for row in self.cursor.fetchall()]
        
        if not ids:
            return 1
        
        # Find first gap
        for i in range(1, max(ids) + 2):
            if i not in ids:
                return i
    
    def get_next_attendance_id(self):
        """Get next available attendance ID (fills gaps)"""
        self.cursor.execute("SELECT attendance_id FROM attendance ORDER BY attendance_id")
        ids = [row[0] for row in self.cursor.fetchall()]
        
        if not ids:
            return 1
        
        # Find first gap
        for i in range(1, max(ids) + 2):
            if i not in ids:
                return i
    
    # ========== STUDENT OPERATIONS ==========
    
    def add_student(self, roll_no, name, class_name, section):
        """Add a new student"""
        try:
            student_id = self.get_next_student_id()
            self.cursor.execute(
                "INSERT INTO students (student_id, roll_no, name, class, section) VALUES (?, ?, ?, ?, ?)",
                (student_id, roll_no, name, class_name, section)
            )
            self.conn.commit()
            print(f"Student added with ID: {student_id}")
        except sqlite3.IntegrityError:
            print("Error: Roll number already exists!")
    
    def view_students(self):
        """Display all students"""
        self.cursor.execute("SELECT * FROM students ORDER BY student_id")
        students = self.cursor.fetchall()
        
        if students:
            print(f"\n{'ID':<5} {'Roll No':<12} {'Name':<20} {'Class':<8} {'Section':<8}")
            print("-" * 53)
            for s in students:
                print(f"{s[0]:<5} {s[1]:<12} {s[2]:<20} {s[3]:<8} {s[4]:<8}")
        else:
            print("No students found!")
    
    def update_student(self, student_id, roll_no=None, name=None, class_name=None, section=None):
        """Update student information"""
        updates = []
        values = []
        
        if roll_no:
            updates.append("roll_no = ?")
            values.append(roll_no)
        if name:
            updates.append("name = ?")
            values.append(name)
        if class_name:
            updates.append("class = ?")
            values.append(class_name)
        if section:
            updates.append("section = ?")
            values.append(section)
        
        if updates:
            values.append(student_id)
            query = f"UPDATE students SET {', '.join(updates)} WHERE student_id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            print("Student updated successfully!")
    
    def delete_student(self, student_id):
        """Delete a student"""
        self.cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        self.conn.commit()
        print("Student deleted successfully!")
    
    # ========== ATTENDANCE OPERATIONS ==========
    
    def mark_attendance(self, roll_no, date, status, reason=""):
        """Mark attendance for a student"""
        # Check if student exists
        self.cursor.execute("SELECT roll_no FROM students WHERE roll_no = ?", (roll_no,))
        if not self.cursor.fetchone():
            print("Error: Student not found!")
            return
        
        # Check if attendance already marked for this date
        self.cursor.execute(
            "SELECT * FROM attendance WHERE roll_no = ? AND date = ?",
            (roll_no, date)
        )
        if self.cursor.fetchone():
            print("Attendance already marked for this date!")
            return
        
        attendance_id = self.get_next_attendance_id()
        self.cursor.execute(
            "INSERT INTO attendance (attendance_id, roll_no, date, status, reason) VALUES (?, ?, ?, ?, ?)",
            (attendance_id, roll_no, date, status, reason)
        )
        self.conn.commit()
        print(f"Attendance marked with ID: {attendance_id}")
    
    def view_attendance_by_date(self, date):
        """View attendance for a specific date"""
        self.cursor.execute("""
            SELECT a.attendance_id, s.roll_no, s.name, s.class, s.section, a.status, a.reason
            FROM attendance a
            JOIN students s ON a.roll_no = s.roll_no
            WHERE a.date = ?
            ORDER BY s.class, s.section, s.roll_no
        """, (date,))
        records = self.cursor.fetchall()
        
        if records:
            print(f"\nAttendance for {date}:")
            print(f"{'ID':<5} {'Roll':<10} {'Name':<20} {'Class':<8} {'Sec':<5} {'Status':<10} {'Reason':<20}")
            print("-" * 78)
            for r in records:
                print(f"{r[0]:<5} {r[1]:<10} {r[2]:<20} {r[3]:<8} {r[4]:<5} {r[5]:<10} {r[6] or '-':<20}")
        else:
            print(f"No attendance records for {date}")
    
    def view_absent_students(self, date):
        """View absent students for a specific date"""
        self.cursor.execute("""
            SELECT s.roll_no, s.name, s.class, s.section, a.reason
            FROM attendance a
            JOIN students s ON a.roll_no = s.roll_no
            WHERE a.date = ? AND a.status = 'Absent'
            ORDER BY s.class, s.section, s.roll_no
        """, (date,))
        records = self.cursor.fetchall()
        
        if records:
            print(f"\nAbsent Students on {date}:")
            print(f"{'Roll No':<12} {'Name':<25} {'Class':<8} {'Section':<8} {'Reason':<25}")
            print("-" * 78)
            for r in records:
                print(f"{r[0]:<12} {r[1]:<25} {r[2]:<8} {r[3]:<8} {r[4] or 'Not specified':<25}")
        else:
            print(f"No absent students on {date}")
    
    def view_present_students(self, date):
        """View present students for a specific date"""
        self.cursor.execute("""
            SELECT s.roll_no, s.name, s.class, s.section
            FROM attendance a
            JOIN students s ON a.roll_no = s.roll_no
            WHERE a.date = ? AND a.status = 'Present'
            ORDER BY s.class, s.section, s.roll_no
        """, (date,))
        records = self.cursor.fetchall()
        
        if records:
            print(f"\nPresent Students on {date}:")
            print(f"{'Roll No':<12} {'Name':<25} {'Class':<12} {'Section':<12}")
            print("-" * 61)
            for r in records:
                print(f"{r[0]:<12} {r[1]:<25} {r[2]:<12} {r[3]:<12}")
        else:
            print(f"No present students on {date}")
    
    def view_by_section(self, class_name, section, date):
        """View attendance by class and section for a date"""
        self.cursor.execute("""
            SELECT a.attendance_id, s.roll_no, s.name, a.status, a.reason
            FROM attendance a
            JOIN students s ON a.roll_no = s.roll_no
            WHERE s.class = ? AND s.section = ? AND a.date = ?
            ORDER BY s.roll_no
        """, (class_name, section, date))
        records = self.cursor.fetchall()
        
        if records:
            print(f"\nAttendance for Class {class_name}-{section} on {date}:")
            print(f"{'ID':<5} {'Roll No':<12} {'Name':<25} {'Status':<10} {'Reason':<20}")
            print("-" * 72)
            for r in records:
                print(f"{r[0]:<5} {r[1]:<12} {r[2]:<25} {r[3]:<10} {r[4] or '-':<20}")
        else:
            print(f"No attendance records for Class {class_name}-{section} on {date}")
    
    def update_attendance(self, attendance_id, status=None, reason=None):
        """Update attendance record"""
        updates = []
        values = []
        
        if status:
            updates.append("status = ?")
            values.append(status)
        if reason is not None:
            updates.append("reason = ?")
            values.append(reason)
        
        if updates:
            values.append(attendance_id)
            query = f"UPDATE attendance SET {', '.join(updates)} WHERE attendance_id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            print("Attendance updated successfully!")
    
    def delete_attendance(self, attendance_id):
        """Delete an attendance record"""
        self.cursor.execute("DELETE FROM attendance WHERE attendance_id = ?", (attendance_id,))
        self.conn.commit()
        print("Attendance record deleted successfully!")
    
    def close(self):
        """Close database connection"""
        self.conn.close()


def get_continue_choice():
    """Ask if user wants to continue"""
    while True:
        choice = input("\nContinue? (yes/no): ").lower()
        if choice in ['yes', 'y']:
            return True
        elif choice in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def main():
    """Main menu"""
    system = AttendanceSystem()
    
    while True:
        print("\n" + "="*50)
        print("ATTENDANCE MANAGEMENT SYSTEM")
        print("="*50)
        print("1. Add Student")
        print("2. View All Students")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Mark Attendance")
        print("6. View Attendance by Date")
        print("7. View Absent Students")
        print("8. View Present Students")
        print("9. View by Section")
        print("10. Update Attendance")
        print("11. Delete Attendance")
        print("0. Exit")
        print("="*50)
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            roll_no = input("Roll Number: ")
            name = input("Name: ")
            class_name = input("Class: ")
            section = input("Section: ")
            system.add_student(roll_no, name, class_name, section)
            
            if not get_continue_choice():
                break
        
        elif choice == '2':
            system.view_students()
            
            if not get_continue_choice():
                break
        
        elif choice == '3':
            student_id = int(input("Student ID: "))
            roll_no = input("New Roll No (blank to skip): ")
            name = input("New Name (blank to skip): ")
            class_name = input("New Class (blank to skip): ")
            section = input("New Section (blank to skip): ")
            system.update_student(
                student_id,
                roll_no if roll_no else None,
                name if name else None,
                class_name if class_name else None,
                section if section else None
            )
            
            if not get_continue_choice():
                break
        
        elif choice == '4':
            student_id = int(input("Student ID to delete: "))
            confirm = input("Confirm delete? (yes/no): ")
            if confirm.lower() == 'yes':
                system.delete_student(student_id)
            
            if not get_continue_choice():
                break
        
        elif choice == '5':
            roll_no = input("Roll Number: ")
            date = input("Date (YYYY-MM-DD) or press Enter for today: ")
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            print("Status: Present / Absent / Late")
            status = input("Status: ")
            reason = input("Reason (if absent): ")
            system.mark_attendance(roll_no, date, status, reason)
            
            if not get_continue_choice():
                break
        
        elif choice == '6':
            date = input("Date (YYYY-MM-DD) or press Enter for today: ")
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            system.view_attendance_by_date(date)
            
            if not get_continue_choice():
                break
        
        elif choice == '7':
            date = input("Date (YYYY-MM-DD) or press Enter for today: ")
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            system.view_absent_students(date)
            
            if not get_continue_choice():
                break
        
        elif choice == '8':
            date = input("Date (YYYY-MM-DD) or press Enter for today: ")
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            system.view_present_students(date)
            
            if not get_continue_choice():
                break
        
        elif choice == '9':
            class_name = input("Class: ")
            section = input("Section: ")
            date = input("Date (YYYY-MM-DD) or press Enter for today: ")
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            system.view_by_section(class_name, section, date)
            
            if not get_continue_choice():
                break
        
        elif choice == '10':
            attendance_id = int(input("Attendance ID: "))
            status = input("New Status (blank to skip): ")
            reason = input("New Reason (blank to skip): ")
            system.update_attendance(
                attendance_id,
                status if status else None,
                reason if reason else None
            )
            
            if not get_continue_choice():
                break
        
        elif choice == '11':
            attendance_id = int(input("Attendance ID to delete: "))
            confirm = input("Confirm delete? (yes/no): ")
            if confirm.lower() == 'yes':
                system.delete_attendance(attendance_id)
            
            if not get_continue_choice():
                break
        
        elif choice == '0':
            system.close()
            print("Thank you!")
            break
        
        else:
            print("Invalid choice!")
    
    system.close()


if __name__ == "__main__":
    main()
