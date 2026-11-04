// 01-csv-over-seriell: Send temperaturmålingar som CSV-linjer over USB.
//
// Arduinoen skriv berre talet, til dømes:
//   21.44
// Python-skriptet logg_til_csv.py les linja, legg til tidspunktet frå datamaskina
// og skriv ei ferdig linje i CSV-fila:
//   2026-11-10 09:15:03,21.44
//
// Linjer som startar med # er meldingar til menneske, og blir ikkje lagra i fila.
//
// Koplinga er den same som i del 1 (DATA på pinne 2, 4,7 kΩ mellom DATA og VCC).

#include <OneWire.h>
#include <DallasTemperature.h>

const int SENSOR_PINNE = 2;
const unsigned long INTERVALL_MS = 5000;  // ei måling kvart 5. sekund

OneWire oneWire(SENSOR_PINNE);
DallasTemperature sensorar(&oneWire);

void setup() {
  Serial.begin(9600);
  while (!Serial && millis() < 5000) {
  }
  sensorar.begin();
  Serial.println("# Temperaturloggar startar");
}

void loop() {
  sensorar.requestTemperatures();
  float temperatur = sensorar.getTempCByIndex(0);

  // Vi sender verdien sjølv om han er -127 (feil). Det er betre å lagre rådata
  // og rydde i etterkant, enn å la data forsvinne utan at vi veit om det.
  Serial.println(temperatur, 2);  // 2 desimalar

  delay(INTERVALL_MS);
}
