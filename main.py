import cv2
import os
import platform
import time

cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()

connected = False


# -----------------------------
# Parse WiFi QR safely
# -----------------------------
def parse_wifi_qr(data):
    # Expected format:
    # WIFI:T:WPA;S:SSID;P:PASSWORD;;
    
    if not data.startswith("WIFI:"):
        return None, None

    data = data.replace("WIFI:", "").strip(";")
    parts = data.split(";")

    ssid = None
    password = None

    for part in parts:
        if part.startswith("S:"):
            ssid = part[2:]
        elif part.startswith("P:"):
            password = part[2:]

    return ssid, password


# -----------------------------
# Connect to WiFi (OS-specific)
# -----------------------------
def connect_wifi(ssid, password):
    system = platform.system()

    print(f"Connecting to WiFi: {ssid}")

    try:
        if system == "Linux":
            # Requires NetworkManager (nmcli)
            cmd = f"nmcli dev wifi connect \"{ssid}\" password \"{password}\""
            return os.system(cmd)

        elif system == "Windows":
            # Windows limitation: must already have a saved WiFi profile
            cmd = f'netsh wlan connect name="{ssid}"'
            return os.system(cmd)

        else:
            print("Unsupported OS")
            return 1

    except Exception as e:
        print("Connection error:", e)
        return 1


# -----------------------------
# Main loop
# -----------------------------
while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    data, bbox, _ = detector.detectAndDecode(frame)

    # Draw QR box if detected
    if bbox is not None:
        for i in range(len(bbox)):
            pt1 = tuple(bbox[i][0].astype(int))
            pt2 = tuple(bbox[(i + 1) % len(bbox)][0].astype(int))
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

    # Handle QR data
    if data:
        print("QR Detected:", data)

        if data.startswith("WIFI:") and not connected:
            ssid, password = parse_wifi_qr(data)

            if not ssid or not password:
                print("Invalid WiFi QR format")
                continue

            result = connect_wifi(ssid, password)

            if result == 0:
                print("✅ Connected successfully!")
                connected = True

                time.sleep(2)
                break
            else:
                print("❌ Failed to connect")

    # Show camera window
    cv2.imshow("WiFi QR Scanner", frame)

    # Press Q to quit manually
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# Cleanup
cap.release()
cv2.destroyAllWindows()
