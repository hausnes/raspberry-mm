// 01-blink: Test at Arduino-kortet, kabelen og programvara fungerer.
// Den innebygde lysdioden (merka "L" eller "LED" på kortet) skal blinke
// ein gong i sekundet, og Serial Monitor skal vise ein teljar.

int teljar = 0;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);  // LED_BUILTIN er pinne 6 på MKR-korta
  Serial.begin(9600);

  // MKR-korta har USB innebygd i sjølve prosessoren. Vi ventar maks 5 sekund
  // på at Serial Monitor blir opna, slik at vi ikkje går glipp av dei første linjene.
  while (!Serial && millis() < 5000) {
  }

  Serial.println("Hei! Arduino-kortet fungerer.");
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH);  // lys på
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);   // lys av
  delay(500);

  teljar = teljar + 1;
  Serial.print("Blink nummer ");
  Serial.println(teljar);
}
