int ledPin = 0;

void setup() {
  // put your setup code here, to run once:
  pinMode(ledPin, OUTPUT); //define ledPin as an output
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(ledPin, HIGH); //turn on an LED
  delay(1000); //as program is paused, with the LED on
  digitalWrite(ledPin, LOW); //program is unpaused, and the LED is turned off
  delay(1000); //program is paused, with the LED off
}
