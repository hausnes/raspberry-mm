// 02-temperatur: Les temperaturen frå ein DS18B20-sensor og skriv han ut.
//
// Kopling (sjå README.md):
//   Raud leidning  (VDD)  -> VCC  (3,3 V) på MKR-kortet
//   Svart leidning (GND)  -> GND
//   Gul leidning   (DATA) -> digital pinne 2
//   4,7 kΩ motstand mellom DATA og VCC (såkalla pull-up-motstand)
//
// Krev biblioteka "OneWire" og "DallasTemperature" (installer via Library Manager).

#include <OneWire.h>
#include <DallasTemperature.h>

const int SENSOR_PINNE = 2;      // pinnen den gule leidningen er kopla til
const int VENTETID_MS = 1000;    // kor lenge vi ventar mellom kvar måling (millisekund)

OneWire oneWire(SENSOR_PINNE);           // set opp 1-Wire-kommunikasjon på pinnen
DallasTemperature sensorar(&oneWire);    // bruk 1-Wire til å snakke med DS18B20

void setup() {
  Serial.begin(9600);
  while (!Serial && millis() < 5000) {
  }

  sensorar.begin();

  Serial.print("Fann ");
  Serial.print(sensorar.getDeviceCount());
  Serial.println(" sensor(ar).");
}

void loop() {
  sensorar.requestTemperatures();               // be sensoren måle (tek ca. 0,75 s)
  float temperatur = sensorar.getTempCByIndex(0); // hent målinga frå sensor nr. 0

  if (temperatur == DEVICE_DISCONNECTED_C) {    // DEVICE_DISCONNECTED_C er -127
    Serial.println("Feil: Fekk ikkje kontakt med sensoren. Sjekk koplinga!");
  } else {
    Serial.print("Temperatur: ");
    Serial.print(temperatur);
    Serial.println(" °C");
  }

  delay(VENTETID_MS);
}
