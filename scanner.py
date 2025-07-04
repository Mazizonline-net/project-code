import cv2
from pyzbar.pyzbar import decode
import sqlite3
from datetime import datetime
import time

DATABASE = 'database.db'

def mark_attendance(index_number):
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute("SELECT id FROM students WHERE index_number = ?", (index_number,))
        result = cur.fetchone()
        if result:
            student_id = result[0]
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            cur.execute("INSERT INTO attendance (student_id, date, time) VALUES (?, ?, ?)",
                        (student_id, date, time_str))
            con.commit()
            print(f"✅ Attendance marked for {index_number} at {time_str} on {date}")
        else:
            print(f"❌ Student with index number {index_number} not found.")

cap = cv2.VideoCapture(0)

scanned_codes = set()
auto_close_delay = 5  # seconds to wait before closing after a successful scan

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    barcodes = decode(frame)
    if barcodes:
        for barcode in barcodes:
            index_number = barcode.data.decode('utf-8')
            if index_number not in scanned_codes:
                mark_attendance(index_number)
                scanned_codes.add(index_number)
                cv2.putText(frame, f"Scanned: {index_number}", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Show the frame with success text for a few seconds
                cv2.imshow('QR Scanner - Auto Closing', frame)
                cv2.waitKey(auto_close_delay * 1000)
                cap.release()
                cv2.destroyAllWindows()
                print("Scanner auto-closed after successful scan.")
                exit()

    cv2.imshow('QR Scanner - Auto Closing', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Scanner manually closed.")
        break

cap.release()
cv2.destroyAllWindows()
