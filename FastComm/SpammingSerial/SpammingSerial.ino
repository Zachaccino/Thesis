int index = 0;
int max_index = 200;


// Given 4 numbers, put them in csv format.
String toCSV(int a, int b, int c, int d) {
  return String(a) + "," + String(b) + "," + String(c) + "," + String(d) + "\n";
}


void setup() {
  Serial.begin(2000000);
}


void loop() {
  // Reset the index.
  if (index > max_index) {
    index = 0;
  }
  
  // Send fake data to serial port.
  // Format: a,b,c,d
  Serial.print(toCSV(index, index+1, index+2, index+3));

  index++;
}
