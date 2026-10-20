
import tkinter as tk
import serial
import threading
import math
import re
import time

# ---------------- CONFIGURATION ----------------

PORT = "COM8"
BAUD_RATE = 9600

MAX_RADIUS = 400
MAX_DISTANCE = 200
ALERT_DISTANCE = 30

BG = "#07111f"
RADAR_GREEN = "#00ff99"
GRID_GREEN = "#155c48"
TEXT_GREEN = "#52b788"
WARNING_RED = "#ff4d6d"
OBJECT_YELLOW = "#ffd166"
MUTED = "#9fb3c8"

# ---------------- WINDOW ----------------

root = tk.Tk()
root.title("EchoScan | Ultrasonic Radar")
root.geometry("800x780")
root.resizable(True, True)
root.resizable(False, False)
root.configure(bg=BG)

canvas = tk.Canvas(
    root,
    width=760,
    height=520,
    bg=BG,
    highlightthickness=0
)
canvas.pack(pady=2)

status_label = tk.Label(
    root,
    text="CONNECTING TO ARDUINO...",
    font=("Consolas", 12, "bold"),
    fg=RADAR_GREEN,
    bg=BG
)
status_label.pack(pady=3)

distance_label = tk.Label(
    root,
    text="Angle: --°   Distance: -- cm",
    font=("Consolas", 14),
    fg="white",
    bg=BG
)
distance_label.pack(pady=3)

nearest_label = tk.Label(
    root,
    text="Nearest object: Searching...",
    font=("Consolas", 12, "bold"),
    fg=TEXT_GREEN,
    bg=BG
)
nearest_label.pack(pady=3)

alert_label = tk.Label(
    root,
    text="SYSTEM STATUS: INITIALIZING",
    font=("Consolas", 13, "bold"),
    fg=RADAR_GREEN,
    bg=BG
)
alert_label.pack(pady=3)

# ---------------- RADAR DATA ----------------

CX, CY = 380, 490

latest_angle = 0
latest_distance = None

# Stores the latest reading at each scan angle.
points = {}

running = True
connection = None

# ---------------- READING UPDATES ----------------

def update_reading(angle, distance):
    global latest_angle, latest_distance

    latest_angle = angle
    latest_distance = distance

    if distance is None or distance < 0:
        points.pop(angle, None)

        distance_label.config(
            text=f"Angle: {angle}°   Distance: No echo",
            fg="white"
        )

    elif distance <= 400:
        if distance <= MAX_DISTANCE:
            points[angle] = distance
        else:
            points.pop(angle, None)

        if distance <= ALERT_DISTANCE:
            distance_label.config(
                text=f"WARNING! {distance:.1f} cm | Angle: {angle}°",
                fg=WARNING_RED
            )
        else:
            distance_label.config(
                text=f"Angle: {angle}°   Distance: {distance:.1f} cm",
                fg="white"
            )

    # Calculate nearest object using available scan readings.
    if points:
        nearest_angle, nearest_distance = min(
            points.items(),
            key=lambda item: item[1]
        )

        nearest_label.config(
            text=(
                f"Nearest object: {nearest_distance:.1f} cm"
                f" | Angle: {nearest_angle}°"
            ),
            fg=(
                WARNING_RED
                if nearest_distance <= ALERT_DISTANCE
                else TEXT_GREEN
            )
        )

        if nearest_distance <= ALERT_DISTANCE:
            alert_label.config(
                text="SYSTEM STATUS: CLOSE OBSTACLE!",
                fg=WARNING_RED
            )
        else:
            alert_label.config(
                text="SYSTEM STATUS: OBJECT DETECTED",
                fg=TEXT_GREEN
            )

    else:
        nearest_label.config(
            text="Nearest object: None detected",
            fg=MUTED
        )

        alert_label.config(
            text="SYSTEM STATUS: NO OBJECTS IN RANGE",
            fg=RADAR_GREEN
        )


# ---------------- DRAW RADAR ----------------

def draw_radar():
    canvas.delete("all")

    # Range rings
    for radius in (100, 200, 300, 400):
        canvas.create_arc(
            CX - radius,
            CY - radius,
            CX + radius,
            CY + radius,
            start=0,
            extent=180,
            outline=GRID_GREEN,
            width=2,
            style="arc"
        )

        range_mark = int(
            MAX_DISTANCE * radius / MAX_RADIUS
        )

        canvas.create_text(
            CX + 8,
            CY - radius + 12,
            text=f"{range_mark} cm",
            fill=TEXT_GREEN,
            font=("Consolas", 9)
        )

    # Horizontal baseline
    canvas.create_line(
        CX - MAX_RADIUS,
        CY,
        CX + MAX_RADIUS,
        CY,
        fill=GRID_GREEN,
        width=2
    )

    # Angle guides
    for angle in range(0, 181, 30):
        radians = math.radians(180 - angle)

        x = CX + MAX_RADIUS * math.cos(radians)
        y = CY - MAX_RADIUS * math.sin(radians)

        canvas.create_line(
            CX, CY, x, y,
            fill="#103b32"
        )

        label_y = (
            y + 12
            if angle in (0, 180)
            else y - 12
        )

        canvas.create_text(
            x,
            label_y,
            text=f"{angle}°",
            fill=TEXT_GREEN,
            font=("Consolas", 10)
        )

    # Object markers
    for angle, distance in list(points.items()):
        if not 0 <= distance <= MAX_DISTANCE:
            continue

        radians = math.radians(180 - angle)
        radius = distance / MAX_DISTANCE * MAX_RADIUS

        x = CX + radius * math.cos(radians)
        y = CY - radius * math.sin(radians)

        close = distance <= ALERT_DISTANCE
        color = WARNING_RED if close else OBJECT_YELLOW
        size = 7 if close else 5

        canvas.create_oval(
            x - size,
            y - size,
            x + size,
            y + size,
            fill=color,
            outline=""
        )

        if close:
            canvas.create_text(
                x,
                y - 15,
                text=f"{distance:.0f}cm",
                fill=WARNING_RED,
                font=("Consolas", 9, "bold")
            )

    # Current scan beam
    radians = math.radians(180 - latest_angle)

    x = CX + MAX_RADIUS * math.cos(radians)
    y = CY - MAX_RADIUS * math.sin(radians)

    canvas.create_line(
        CX,
        CY,
        x,
        y,
        fill=RADAR_GREEN,
        width=3
    )

    canvas.create_oval(
        CX - 5,
        CY - 5,
        CX + 5,
        CY + 5,
        fill=RADAR_GREEN,
        outline=""
    )

    # Radar heading and legend
    canvas.create_text(
        155,
        25,
        text="ECHOSCAN | LIVE RADAR",
        fill=RADAR_GREEN,
        font=("Consolas", 12, "bold")
    )

    canvas.create_text(
        160,
        48,
        text="Yellow: Object   Red: Close obstacle",
        fill=MUTED,
        font=("Consolas", 9)
    )

    root.after(50, draw_radar)


# ---------------- ARDUINO CONNECTION ----------------

def read_arduino():
    global connection, running

    try:
        connection = serial.Serial(
            PORT,
            BAUD_RATE,
            timeout=1
        )

        time.sleep(2)

        root.after(
            0,
            lambda: status_label.config(
                text=f"CONNECTED | Arduino on {PORT}",
                fg=RADAR_GREEN
            )
        )

        while running:
            line = connection.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            # Expected: 40, 25.4 cm
            match = re.match(
                r"^\s*(\d{1,3})\s*,\s*"
                r"([-+]?\d+(?:\.\d+)?)\s*cm\s*$",
                line,
                re.IGNORECASE
            )

            if match:
                angle = int(match.group(1))
                distance = float(match.group(2))

                if 0 <= angle <= 180 and 0 <= distance <= 400:
                    root.after(
                        0,
                        lambda a=angle, d=distance:
                        update_reading(a, d)
                    )

                continue

            # Expected: 40, No echo
            no_echo = re.match(
                r"^\s*(\d{1,3})\s*,\s*No echo\s*$",
                line,
                re.IGNORECASE
            )

            if no_echo:
                angle = int(no_echo.group(1))

                if 0 <= angle <= 180:
                    root.after(
                        0,
                        lambda a=angle:
                        update_reading(a, None)
                    )

    except Exception as error:
        message = str(error)

        root.after(
            0,
            lambda m=message:
            status_label.config(
                text=f"CONNECTION ERROR: {m}",
                fg=WARNING_RED
            )
        )


# ---------------- SAFE SHUTDOWN ----------------

def close_app():
    global running

    running = False

    if connection and connection.is_open:
        connection.close()

    root.destroy()


# ---------------- START APPLICATION ----------------

root.protocol("WM_DELETE_WINDOW", close_app)

threading.Thread(
    target=read_arduino,
    daemon=True
).start()

draw_radar()
root.mainloop()
