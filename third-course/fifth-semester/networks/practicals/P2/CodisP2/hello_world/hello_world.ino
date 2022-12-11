String incomingData;
boolean TransmisioCompleta = false;

void setup() {
    Serial.begin(9600);
    delay(1000);
    Serial.println("Hello world");
}

void loop() {
    if (Serial.available()) {
        Serial.print(" > ");
        Serial.println(Serial.readString());
    }
}
