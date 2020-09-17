int a = 0;
int b = 20;
int pwm = 0;
int maxm = 250;
int i = 0;
int state = 0;
int distance = 0;
void setup() {
  pinMode(11, INPUT_PULLUP);
  pinMode(12, INPUT_PULLUP);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);

  Serial.begin(9600);
  Serial.setTimeout(3);

}
void loop() {
  /*
    if (!digitalRead(11)) {
    analogWrite(5, 0);
    analogWrite(6, a);

    }

    else if (!digitalRead(12)) {
    analogWrite(5, a);
    analogWrite(6, 0);
    }
    else {
    analogWrite(5, a);
    analogWrite(6, a);

    }*/
  if (Serial.available() > 0) {
    distance = Serial.parseInt();
  }
  if (distance != 0) {
    if (abs(distance) > 10) {
      a = maxm;
      if (a > pwm) {
        pwm = min(pwm + min(a - pwm, b), maxm);
      }
      else {
        pwm = max(pwm - min(pwm - a, b), 0);
      }
    }
    else {
      a = (maxm / 10) * abs(distance);
      if (a > pwm) {
        pwm = min(pwm + min(a - pwm, 1), maxm);
      } else {
        pwm = max(pwm - min(pwm - a, 1), 0);
      }
    }
  }
  else {
    a = 0;
    if (pwm >= 30) {
      pwm = max(pwm - min(pwm - a, b), 0);
    }
    else  {
      pwm = max(pwm - min(pwm - a, 1), 0);
    }
  }
  if (distance > 0) {
    analogWrite(5, 0);
    analogWrite(6, pwm);
    state = 0;
  }
  if (distance < 0) {
    analogWrite(5, pwm);
    analogWrite(6, 0);
    state = 1;
  }
  if (distance != 0) {
    distance = distance - (distance / abs(distance));
  }
  if (distance == 0) {

    if (abs(pwm) < 1) {
      analogWrite(5, 0);
      analogWrite(6, 0);
    }
    else {
      if (state) {
        analogWrite(5, pwm);
        analogWrite(6, 0);
      } else {
        analogWrite(5, 0);
        analogWrite(6, pwm);
      }
    }
  }
  Serial.print(distance);
  Serial.print(",");
  Serial.println(pwm);
  delay(100);
}
/*
  #define Pulse 5
  #define Dir 6
  long delay_Micros =1800; // Set value
  long currentMicros = 0; long previousMicros = 0;
  void setup()
  {
  pinMode(Pulse,OUTPUT);
  pinMode(Dir,OUTPUT);
  pinMode(11, INPUT_PULLUP);
  pinMode(12, INPUT_PULLUP);
  digitalWrite(Dir,LOW);
  }
  void loop()
  {
  if (!digitalRead(11)){
  currentMicros = micros();
  if(currentMicros - previousMicros >= delay_Micros)
  {
  previousMicros = currentMicros;
  digitalWrite(Pulse,HIGH);
  delayMicroseconds(400); //Set Value
  digitalWrite(Pulse,LOW); }
  } }*/
