#include <Arduino_MKRGPS.h> // Bibliotek som leser av GPS
#include <MKRNB.h>          // Bibliotek som overførerdata til server via GPRS
#include <SPI.h>            // Bibilotek for håndtering av serie-bus

long Pause                 = 5000; // En ev. pause i programloopen

float GPSlat               = 0;    // GPS breddegrad
float GPSlong              = 0;    // GPS lengdegrad
unsigned long epochTime    = 0;    // GPS tidsstempel fra 1.1.1980
int numSat                 = 0;    // GPS antall satellitter
int maxNoChecks            = 5000; // Antall runder for lesing av GPS-data


void setup() {
  Serial.begin(115200);       // Setter opp data hastighet til monitor

  GPS.begin();              // Initialisering av GPS
  SPI.begin();
}

void loop() {
  readGPSdata1();       // Inkluder GPS
  printGPS();           // Skriv ut GPS-data
  delay(Pause);         // Ev. legg inn en pause i loopen 

}

// Funksjonen leser av GPS-data ved bruk av while
void readGPSdata()
{
    while (!GPS.available()) {}  //stopper opp om ikke kontakt med gps. 

    GPSlat   = GPS.latitude();
    GPSlong  = GPS.longitude();
    epochTime  = GPS.getTime(); 
    numSat = GPS.satellites(); 
}

// Funksjonen leser av GPS-data med bruk av en for-loop
void readGPSdata1()
{
  int noChecks = 0;
  
  Serial.println("Leser GPS");

  for (int i = 0; i < maxNoChecks; i++)
  {
    // Check if there is new GPS data available
    if (GPS.available())
    {
  
      // If there is, read GPS values
      GPSlat   = GPS.latitude();
      GPSlong  = GPS.longitude();
      epochTime  = GPS.getTime();
      numSat = GPS.satellites();

      Serial.print("Antall GPS sjekk: ");
      Serial.println(noChecks);
      
      break;
    }

    noChecks++;
    
      if (noChecks == maxNoChecks) Serial.println("Mislykket henting av posisjon fra GPS");
      
  }
}

void printGPS(){
  Serial.print("Breddegrad: "); Serial.println(GPSlat,6);
  Serial.print("Lengdegrad: "); Serial.println(GPSlong,6);
  Serial.print("Epoketid  : "); Serial.println(epochTime);
  Serial.print("Antall sat: "); Serial.println(numSat);
  Serial.println();
}
