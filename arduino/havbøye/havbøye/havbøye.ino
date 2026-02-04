

void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:

  
  

}

// Given a number of seconds since 1.1.1980, calculate the date and time
// and print it to the serial port.
void printDateTime(unsigned long seconds) {
	// Calculate date and time values
	byte second = seconds % 60;
	byte minute = (seconds / 60) % 60;
	byte hour = (seconds / 3600) % 24;
	byte dayOfWeek = ((seconds / 86400) + 4) % 7; // Jan 1, 1980 was a Thursday
	unsigned int days = seconds / 86400;
	byte year;
	byte month, monthLength;
	unsigned int yearLength;
	for (year = 0; ; year++) {
		yearLength = isLeapYear(year) ? 366 : 365;
		if (days >= yearLength) {
			days -= yearLength;
		} else {
			break;
		}
	}
	for (month = 0; ; month++) {
		monthLength = monthDays(month, year);
		if (days >= monthLength) {
			days -= monthLength;
		} else {
			break;
		}
	}
	byte day = days + 1;
	// Print date and time
	Serial.print(day, DEC);
	Serial.print('/');
	Serial.print(month + 1, DEC);
	Serial.print('/');
	Serial.print(year + 1980, DEC);
	Serial.print(" (");
	Serial.print(dayOfWeekStr(dayOfWeek));
	Serial.print(") ");
	Serial.print(hour, DEC);
	Serial.print(':');
	Serial.print(minute, DEC);
	Serial.print(':');
	Serial.print(second, DEC);
	Serial.println();
}