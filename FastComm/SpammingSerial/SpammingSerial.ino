int fakeDataStore1[200]; 
int fakeDataStore2[200]; 
int fakeDataStore3[200]; 
int fakeDataStore4[200]; 
int i = 0;
int m = 200;

void setup() {
  Serial.begin(9600);
}

void loop() {
  fakeDataStore1[i] = i;
  fakeDataStore2[i] = i;
  fakeDataStore3[i] = i;
  fakeDataStore4[i] = i;
  i++;

  if (i >= m) {
    i = 0;
  }
  

  Serial.print("10000000000\n");
}
