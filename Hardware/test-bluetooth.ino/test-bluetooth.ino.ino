int counter =0;
char INBYTE;
void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);
  delay(50);
}
 
void loop() {
  counter++;
  Serial.println("Press 1 to turn on LED and 0 to turn off ");
  while (true){
    if (Serial.available()){
      break;
    }
  }
  INBYTE = Serial.read();
  if (INBYTE == '0'){
    digitalWrite(13, LOW);
 
  }
  if (INBYTE == '1'){
    digitalWrite(13, HIGH);
  }
  Serial.println(counter);
  delay(50); // wait half a sec
}
