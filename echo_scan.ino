
#include <Servo.h>

const int trigPin = 9;
const int echoPin = 10;
const int servoPin = 6;
const int buzzerPin = 8;
const int ledPin = 7;

const float alertDistance = 30.0;

Servo radarServo;

float getDistance() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000);

  if (duration == 0) return -1;

  float distance = duration * 0.0343 / 2.0;

  if (distance < 2 || distance > 400) {
    return -1;
  }

  return distance;
}

void scanAtAngle(int angle) {
  radarServo.write(angle);
  delay(250);

  float distance = getDistance();

  if (distance >= 0 && distance <= alertDistance) {
    tone(buzzerPin, 1000);
    digitalWrite(ledPin, HIGH);
  } else {
    noTone(buzzerPin);
    digitalWrite(ledPin, LOW);
  }

  Serial.print(angle);
  Serial.print(", ");

  if (distance >= 0) {
    Serial.print(distance, 1);
    Serial.println(" cm");
  } else {
    Serial.println("No echo");
  }
}

void setup() {
  Serial.begin(9600);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(ledPin, OUTPUT);

  digitalWrite(ledPin, LOW);

  radarServo.attach(servoPin);

  Serial.println("EchoScan Radar Started!");
  Serial.println("Angle, Distance (cm)");
}

void loop() {
  for (int angle = 0; angle <= 180; angle += 10) {
    scanAtAngle(angle);
  }

  for (int angle = 180; angle >= 0; angle -= 10) {
    scanAtAngle(angle);
  }

  noTone(buzzerPin);
  digitalWrite(ledPin, LOW);
}
