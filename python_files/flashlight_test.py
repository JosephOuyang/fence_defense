import cv2

cap = cv2.VideoCapture(0)
print("cap opened:", cap.isOpened())
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(gray)
    x, y = maxLoc

    cv2.circle(frame, (x, y), 20, (0, 0, 255), 2)
    cv2.imshow("Flashlight Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()