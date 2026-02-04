int teller = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600); //initialize serial communication
  Serial.println("Programmet har starta.");
}

void loop() {
  // put your main code here, to run repeatedly:
  teller++;
  Serial.println("Dette køyrer i ein loop, no har denne koden køyrt " + String(teller) + " antall gonger.");
  delay(500);
}