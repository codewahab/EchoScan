
# EchoScan — Ultrasonic Radar with Python

EchoScan is an Arduino-based ultrasonic scanning system that measures distances to nearby objects and visualizes the results through a Python radar interface.

## Features

- 180-degree servo scanning
- HC-SR04 ultrasonic distance measurement
- Real-time Python radar visualization
- Serial communication between Arduino and Python
- LED and buzzer alerts for nearby obstacles
- Closest-object monitoring and system status display

## Hardware Used

- Arduino Uno R3
- HC-SR04 ultrasonic sensor
- SG90 servo motor
- Piezo buzzer
- LED and resistor
- Breadboard and jumper wires
- Computer running Python

## Wiring

| Component | Arduino Pin |
|---|---|
| Ultrasonic TRIG | D9 |
| Ultrasonic ECHO | D10 |
| Servo signal | D6 |
| Buzzer positive | D8 |
| LED signal (through resistor) | D7 |
| VCC | 5V |
| GND | GND |

## Software

- Arduino IDE
- Python
- pyserial
- matplotlib

## Setup

1. Connect the hardware according to the wiring table.
2. Open `echo_scan.ino` in the Arduino IDE.
3. Select the correct Arduino board and serial port.
4. Upload the sketch to the Arduino.
5. Install Python dependencies:

   ```bash
   py -m pip install -r requirements.txt
   ```

6. Close the Arduino IDE Serial Monitor.
7. Run the radar application:

   ```bash
   py echoscan.py
   ```

If your Arduino uses a different serial port, update the port setting in `echoscan.py`.

## Screenshot

See the `SS` folder for a screenshot of the Python radar interface.

## How It Works

The servo rotates the ultrasonic sensor through a scanning range. The sensor measures the distance to objects, and the Arduino sends angle and distance readings to the Python application. The application plots the readings on a radar-style display.

The buzzer and LED provide proximity alerts when an object is within the configured alert distance.

## Limitations

This is an ultrasonic radar-style scanner, not a conventional radio-frequency radar. It detects objects based on ultrasonic reflections and cannot identify whether an object is a person, vehicle, or another object.

## Project Status

Functional prototype. Further improvements may include detection filtering, event logging, and enhanced visualization.

## Author

Created as a personal Electronics and Computing project.