#include "ESP8266WiFi.h"

String ssid, password; 

void setup() {
    Serial.begin(115200);
    WiFi.mode(WIFI_STA); 
    WiFi.disconnect();
}

void loop() {

    print_menu();

    switch (get_option()) {
        case 1: scan(); break;
        case 2: connect_to_network(); break;
        case 3: get_RSSI(); break;
        case 4: disconnect_from_network(); break;
        default: Serial.println("Invalid option"); break;
    }

}

int get_option() {
    while (!Serial.available());
    return Serial.readString().toInt();
}

void scan() {
    int n = WiFi.scanNetworks();
    if (n == 0) Serial.println("No networks found");
    else {
        for (int i = 0; i < n; i++) {
            Serial.print(i + 1);
            Serial.print(" ");
            Serial.print(WiFi.SSID(i));
            Serial.print("(");
            Serial.print(WiFi.RSSI(i));
            Serial.print(")");
            Serial.println((WiFi.encryptionType(i) == ENC_TYPE_NONE) ? " " : "*");
            delay(10);
        }
    }
}

void print_menu() {
    Serial.println("\n1. Scan networks");
    Serial.println("2. Connect to network");
    Serial.println("3. Get RSSI");
    Serial.println("4. Disconnect from network\n");
}

void connect_to_network() {

    if (WiFi.status() != WL_CONNECTED) {
        wifiNetworkSelection(); 
  
        ssid = ssid.substring(0, ssid.length() - 1);
        password = password.substring(0, password.length() - 1);
  
        char cssid[ssid.length()];
        char cpsw[password.length()];
  
        ssid.toCharArray(cssid, ssid.length() + 1);
        password.toCharArray(cpsw, password.length() + 1);
  
        connectToWiFi(cssid, cpsw);
    } 
    
    else Serial.println("You are already connected");
    
}

void get_RSSI() {
    if (WiFi.status() == WL_CONNECTED) Serial.println(WiFi.RSSI());
    else Serial.println("Not connected\n");
}

void disconnect_from_network() {
    if (WiFi.status() == WL_CONNECTED) WiFi.disconnect(); 
    Serial.println("Disconnected");
}

void connectToWiFi(char cssid[], char cpsw[]) {
    if (WiFi.status() != WL_CONNECTED) {
        WiFi.begin(cssid, cpsw);
        int contador = 0;
        while (WiFi.status() != WL_CONNECTED) {
            delay(1000);
            Serial.println("Connecting...");
            if (contador++ == 10) break;
        }
        Serial.println(WiFi.localIP()); 
    }
}

void wifiNetworkSelection() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("SSID:");
        while (!Serial.available());
        ssid = Serial.readString();
    
        Serial.print("Password:");
        while (!Serial.available());
        password = Serial.readString();
    }
}
