// 02-sd-kort: Logg temperatur til ei CSV-fil på SD-kort (MKR MEM Shield).
//
// Arduinoen har inga klokke som veit kva dato og klokkeslett det er. Derfor
// lagrar vi "sekund sidan start". Skriv ned når du starta loggaren, så kan du
// rekne om til ekte tidspunkt i Python etterpå (sjå README.md).
//
// Kvar gong kortet startar, lagar det ei ny fil: LOGG00.CSV, LOGG01.CSV, ...
// Då startar sekundteljinga på 0 i kvar fil, og ingen målingar blir blanda.
//
// Krev biblioteka "OneWire", "DallasTemperature" og "SD".

#include <SPI.h>
#include <SD.h>
#include <OneWire.h>
#include <DallasTemperature.h>

const int SENSOR_PINNE = 2;
const int SD_CS_PINNE = 4;                  // MKR MEM Shield brukar pinne 4 for SD-kortet
const unsigned long INTERVALL_MS = 10000;   // ei måling kvart 10. sekund

OneWire oneWire(SENSOR_PINNE);
DallasTemperature sensorar(&oneWire);

char filnamn[] = "LOGG00.CSV";   // SD-biblioteket taklar berre korte filnamn (8 + 3 teikn)

// Blinkar fort for alltid. Brukt når noko er gale, slik at vi ser det utan PC.
void feil() {
  pinMode(LED_BUILTIN, OUTPUT);
  while (true) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(100);
    digitalWrite(LED_BUILTIN, LOW);
    delay(100);
  }
}

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
  while (!Serial && millis() < 5000) {
  }

  sensorar.begin();

  if (!SD.begin(SD_CS_PINNE)) {
    Serial.println("Fann ikkje SD-kortet. Sit det heilt inne? Er det formatert som FAT32?");
    feil();
  }

  // Finn første ledige filnamn: LOGG00.CSV, LOGG01.CSV, ... LOGG99.CSV
  for (int i = 0; i < 100; i++) {
    filnamn[4] = '0' + i / 10;
    filnamn[5] = '0' + i % 10;
    if (!SD.exists(filnamn)) {
      break;
    }
  }

  File fil = SD.open(filnamn, FILE_WRITE);
  if (!fil) {
    Serial.println("Klarte ikkje å lage fila.");
    feil();
  }
  fil.println("sekund,temperatur");  // overskriftslinja
  fil.close();

  Serial.print("Loggar til ");
  Serial.println(filnamn);
}

void loop() {
  sensorar.requestTemperatures();
  float temperatur = sensorar.getTempCByIndex(0);
  unsigned long sekund = millis() / 1000;

  File fil = SD.open(filnamn, FILE_WRITE);  // FILE_WRITE legg til på slutten av fila
  if (fil) {
    fil.print(sekund);
    fil.print(",");
    fil.println(temperatur, 2);
    fil.close();  // lukk fila kvar gong, så mistar vi minst mogleg om straumen går

    // eitt kort blink = målinga er lagra
    digitalWrite(LED_BUILTIN, HIGH);
    delay(50);
    digitalWrite(LED_BUILTIN, LOW);
  } else {
    Serial.println("Klarte ikkje å opne fila!");
  }

  Serial.print(sekund);
  Serial.print(",");
  Serial.println(temperatur, 2);

  delay(INTERVALL_MS);
}
