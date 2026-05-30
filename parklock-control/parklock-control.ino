#define enA 6
#define in1 4
#define in2 5
#define button 2
#define button2 3
#define sensor1 7
#define sensor2 8

int rotSpeed = 0;
bool pressed1 = false;
bool pressed2 = false;

bool sens1 = false;
bool sens2 = false;

void setup() {
  pinMode(enA, OUTPUT);
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(button, INPUT);
  pinMode(button2, INPUT);
  pinMode(sensor1, INPUT);
  pinMode(sensor2, INPUT);
  // Set initial rotation direction
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);

  // start serial port at 9600 bps and wait for port to open:
  Serial.begin(9600);
  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
  }
}

void loop() {
  pressed1 = digitalRead(button) == 1;
  pressed2 = digitalRead(button2) == 1;
  
  sens1 = digitalRead(sensor1) == 1;
  sens2 = digitalRead(sensor2) == 1;

  if (pressed1) {
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
    rotSpeed = 1;
    delay(20);
  } else if (pressed2) {
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
    rotSpeed = 1;
    delay(20);
  } else {
    rotSpeed = 0;
  }
  if (rotSpeed == 1) {
    analogWrite(enA, 255);
  } else {
    analogWrite(enA, 0);
  }
  
  Serial.print(sens1);
  Serial.print(",");
  Serial.print(sens2);
  Serial.print(",");
  Serial.println(rotSpeed);
  delay(200);
}