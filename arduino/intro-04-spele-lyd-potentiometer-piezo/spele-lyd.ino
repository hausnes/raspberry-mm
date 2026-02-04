int sensorVerdi = 0;

void setup()
{
    pinMode(A5, INPUT);
    pinMode(8, OUTPUT);
    Serial.begin(9600);
}

void loop()
{
    sensorVerdi = analogRead(A5);
    if (sensorVerdi == 0) {
        noTone(8);
    }
    tone(8, sensorVerdi);
    Serial.println(sensorVerdi);
    delay(10); // Delay a little bit to improve simulation performance
}