import cv2
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
TARGET = ("127.0.0.1", 5005)

cap = cv2.VideoCapture(0)
print("Camera opened?", cap.isOpened())
print("Resolution:", cap.get(3), "x", cap.get(4))
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # get brightest point
    _, _, _, maxLoc = cv2.minMaxLoc(gray)
    x, y = maxLoc

    # send coordinates to CMU Graphics
    sock.sendto(f"{x},{y}".encode(), TARGET)

cap.release()