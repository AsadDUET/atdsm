int target_pwm=0;
int pwm = 0;
int maxm = 220;
int state=0;
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
  if (Serial.available() > 0) {
    distance = Serial.parseInt();}
    target_pwm=f_target_pwm(distance);
    if (distance>0){
      if (!digitalRead(11)){
        target_pwm=0;
      }
    }
    if (distance<0){
      if(!digitalRead(12)){
        target_pwm=0;
      }
    }

  if (target_pwm!=pwm){
    if (target_pwm>pwm){
      pwm=pwm+delta(pwm);
    }
    else {
      pwm=pwm-delta(pwm);
    }
  }
  run(pwm);
  /*
  Serial.print(pwm);
  Serial.print(',');
  Serial.println(distance);*/

  delay(50);
}
void run(int val){
  if (val>0){
    analogWrite(5, 0);
    analogWrite(6, val);
    state=1;
  }
  else if (val<0){
    analogWrite(5, abs(val));
    analogWrite(6, 0);
    state=-1;
  }
  else{
    analogWrite(5, val);
    analogWrite(6, val);
    state=0;
  }
}
int f_target_pwm(int val){
  if (val>=-10 && val<=10)
  return (maxm/10)*val;
  else if(val<-10)
  return -maxm;
  else if(val>10)
  return maxm;
}
int delta(int val){
  if (abs(val)<=11)
  return 1;
  else if (abs(val)>10)
  return min(abs(abs(val)-10),min(10,abs(target_pwm-val)));


}
