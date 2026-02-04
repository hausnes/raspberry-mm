// Programmet er skrevet av Thor Inge Hansen
// Programmet er modifisert av Nils Kr. Rossing
// 29.05.23 - Montert ENV-kort og testet SD-kort (nkr)
// 25.07.23 - Lagt inn mulighet til å velge bort MKR ENV dersom dette ikke er tilkoblet (nkr)
// 25.07.23 - Oppdatert filen med kommentarer (nkr)


#include <DS18B20.h>
#include <OneWire.h>
#include <Arduino_MKRENV.h>
#include <SPI.h>
#include <SD.h>
#include <Arduino_MKRGPS.h>
#include <MKRNB.h>
#include <WDTZero.h>

WDTZero myWDT;
NBClient client;
GPRS gprs;
NB nbAccess;
DS18B20 ds(0);
File myFile;

//#define printState; // Kommenter ut for å slå av alle Serial print
//#define MKR_ENV;    // Kommenter ut dersom kortet MKR ENV ikke brukes

uint8_t address[] = { 40, 250, 31, 218, 4, 0, 0, 52 };
uint8_t selected;
char server[] = "sensor.marin.ntnu.no";
char path[] = "/cgi-bin/tof.cgi?";
char filename[] = "EVU-kurs.txt";
int port = 80;
bool connected = false;  // Status oppkobling
char buffer[128];

unsigned long pause = 1000 * 60 * 6;  //6 min
int shutOffPin = 1;                   // Port til shutOffPin
float w_temperature = 0;
float GPSlat = 0;
float GPSlong = 0;
unsigned long epochTime;
int numSat = 0;
float temperature = 0;
float humidity = 0;
float pressure = 0;
float illuminance = 0;
float battVolt = 0;

void setup() {
  pinMode(shutOffPin, OUTPUT);
  digitalWrite(shutOffPin, HIGH);
#ifdef printState
  Serial.begin(9600);
  while (!Serial) {}
  Serial.println("Ferdig_program_med_PICAXE_MILLIS_TEST_2");
#endif

  analogReadResolution(12);  // 12Bits

  myWDT.attachShutdown(shutDownFunc);  // Initialiser intern vakthund 
  myWDT.setup(WDT_SOFTCYCLE2M);        // Sett toimeout vakthund til ca. 2 minutter (128 sek)

  while (!GPS.begin()) {}              // Initialiser GPS-mottakeren

  readWaterTemp();

  readGPSdata();        // Les GPS data
  delay(500);
  readENVData();
  delay(1000);          // Delay for å få stabile spenningsverdier
  readBattVoltage();    // Les batterispenning
  delay(1000);
  makeString();         // Bygg opp bufferet
  sdPrint();            // Skriv til SD-kort
#ifdef printState
  serialPrint();
#endif
  connectToGPRS();      // Koble opp mot 4G (GPRS)
  connectToServer();    // Koble opp til server
  delay(1000);
#ifdef printState
  Serial.println(millis());
#endif
  digitalWrite(shutOffPin, LOW);  //Be PICAXE om å slå av spenningen
}

// Les av vanntemperatur
void readWaterTemp() {
  w_temperature = ds.getTempC();
}

// Les av batterisepenningen
void readBattVoltage() {
  //Forutsetter lik deling av batterispenning mellom to like resistorer og at A1 brukes
  battVolt = analogRead(A1) * 2 * 3.3 / 4096;
}

// Les av GPS-data
void readGPSdata() {

#ifdef printState
  Serial.println("Started readGPSdata");
#endif

  while (!GPS.available()) {}  // vent til GPS er tilgjengelig

  GPSlat = GPS.latitude();
  GPSlong = GPS.longitude();
  epochTime = GPS.getTime();
  numSat = GPS.satellites();
}

// Les av miljødata
void readENVData() {
#ifdef MKR_ENV
  ENV.begin();
  temperature = ENV.readTemperature();
  humidity = ENV.readHumidity();
  pressure = ENV.readPressure();
  illuminance = ENV.readIlluminance();
#endif
}

// Bygg opp databufferet for overføring til server
void makeString() {
  sprintf(buffer, "%s%s,%u,%.6f,%.6f,%i,%.1f,%.1f,%.1f,%.1f,%.2f,%.2f", path, filename, epochTime, GPSlat, GPSlong, numSat, temperature, w_temperature, humidity, pressure, illuminance, battVolt);
}

// Koble til 4G GPRS
void connectToGPRS() {
#ifdef printState
  Serial.println("Started connectToGPRS()");
#endif

  while (!connected) {
    if ((nbAccess.begin("", true, true) == NB_READY) && (gprs.attachGPRS() == GPRS_READY)) {
      connected = true;
#ifdef printState
      Serial.println("GPRS connected");
#endif
    } else {
      delay(1000);
#ifdef printState
      Serial.println("connected still False");
#endif
    }
  }
}

// Koble til server
void connectToServer() {
#ifdef printState
  Serial.println("in connectToServer()");
#endif

  if (client.connect(server, port)) {
#ifdef printState
    Serial.println("Connected to Server");
#endif

    client.print("GET ");  // Gjør et HTTP request:
    client.print(buffer);
    client.print(',');
    client.print(millis() + 10271);  //Prints runtime + set delay + calculated offset to show the runtime untill shuOffPin turns low
    client.println(" HTTP/1.1");
    client.print("Host: ");
    client.println(server);
    client.println("Connection: close");
    client.println();

#ifdef printState
    Serial.println("String uploaded to Server");
#endif
  } else {

#ifdef printState
    Serial.println("No connection to server");
#endif
  }
}

// Skriv data-bufferet til SD-kort
void sdPrint() {

  if (!SD.begin(4))
    while (1)
      ;  //STOPP OPP

  myFile = SD.open("EVU-kurs.txt", FILE_WRITE);

  if (myFile) {
    myFile.println(buffer);
    myFile.close();
  }
}

// Skriv ut databufferet til monitoren
void serialPrint() {
#ifdef printState
  Serial.println(buffer);
#endif
}

// Funksjon som ber PICAXE slå av spenningen
void shutDownFunc() {
  digitalWrite(shutOffPin, LOW);
  delay(5000);
}

void loop() {}
