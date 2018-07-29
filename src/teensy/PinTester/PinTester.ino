int current_pin;

void setup() {
  Serial.begin(9600);
  setPin(13);
}

void loop() {
  if(Serial.available()) {
    int pin = Serial.parseInt();
    setPin(pin);
    while(Serial.available()) {
      Serial.read();
    }
  }
  digitalWrite(current_pin, HIGH);
  delay(300);
  digitalWrite(current_pin, LOW);
  delay(300);
}

void setPin(int new_pin) {
  Serial.println(String("setting pin to ") + new_pin);
  digitalWrite(current_pin, LOW);
  current_pin = new_pin;
  pinMode(current_pin, OUTPUT);
}

