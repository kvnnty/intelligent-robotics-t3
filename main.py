import cv2
import serial
import time
import numpy as np

# Initialize serial communication with Arduino (COM5 for windows)
try:
    ser = serial.Serial('COM5', 9600, timeout=1)
    time.sleep(2)
except serial.SerialException as e:
    print(f"Serial connection error: {e}")
    exit(1)

# Load the pre-trained Haar cascade classifier for stop signs
CLASSIFIER_PATH = './classifier/stop_sign_cascade_classifier.xml'
stop_cascade = cv2.CascadeClassifier(CLASSIFIER_PATH)
if stop_cascade.empty():
    print("Error: Could not load cascade classifier.")
    exit(1)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    ser.close()
    exit(1)

stop_signal_start = 0
stop_signal_duration = 3  # Send stop signal for 3 seconds
is_stopping = False

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect stop signs in the frame
        stop_signs = stop_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50)
        )

        # Draw rectangles around detected stop signs
        for (x, y, w, h) in stop_signs:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(frame, 'Stop Sign', (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # Logic for sending serial signals
        current_time = time.time()
        if len(stop_signs) > 0 and not is_stopping:
            # Stop sign detected, send '1' and start timer
            ser.write(b'1\n')
            stop_signal_start = current_time
            is_stopping = True
            print("Stop sign detected, sending '1'")
        elif is_stopping and (current_time - stop_signal_start) < stop_signal_duration:
            # Continue sending '1' for 3 seconds
            ser.write(b'1\n')
            print("Continuing to send '1' for stop signal")
        else:
            # Send '0' to resume movement
            ser.write(b'0\n')
            is_stopping = False
            if len(stop_signs) == 0:
                print("No stop sign, sending '0'")
    
        cv2.imshow('Stop Sign Detection', frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.01)

except KeyboardInterrupt:
    print("Program terminated by user.")

finally:
    # Cleanup
    print("Cleaning up...")
    cap.release()
    cv2.destroyAllWindows()
    ser.write(b'0\n')  # Ensure robot stops on exit
    print("Stopping robot and releasing resources.")
    ser.close()
    print("Resources released.")