#include <SPI.h>
#include <UIPEthernet.h>

byte mac[] = {0x02,0x13,0x37,0xAA,0xBB,0xCC};

IPAddress ip(10,8,34,177);
IPAddress gateway(10,8,32,1);
IPAddress subnet(255,255,248,0);
IPAddress dnsServer(10,8,32,1);

IPAddress server(10,8,34,16); // PC

const int led = 22;
const int botao1 = 24;
const int botao2 = 26;

EthernetClient client;

void setup() {
  Serial.begin(9600);

  pinMode(botao1, INPUT_PULLUP);
  pinMode(botao2, INPUT_PULLUP);
  pinMode(led, OUTPUT);

  Serial.println("Inicializando rede...");

  Ethernet.begin(mac, ip, dnsServer, gateway, subnet);

  delay(1000);

  Serial.print("IP: ");
  Serial.println(Ethernet.localIP());

  digitalWrite(led, HIGH);
}

void enviarComando(const char* comando) {
  Serial.print("Enviando: ");
  Serial.println(comando);

  if (client.connect(server, 8000)) {
    Serial.println("CONECTOU!");

    // HTTP SIMPLES (mais compatível)
    client.print("GET /");
    client.print(comando);
    client.println(" HTTP/1.0");

    client.println("Host: 10.8.34.16");
    client.println();

    delay(100);

    // Debug da resposta
    while (client.available()) {
      char c = client.read();
      Serial.write(c);
    }

    client.stop();
    Serial.println("\nComando enviado!");
  } else {
    Serial.println("FALHA AO CONECTAR");
  }
}

void loop() {

  if (digitalRead(botao1) == LOW) {
    enviarComando("bloquear");
    delay(300);
  }

  if (digitalRead(botao2) == LOW) {
    enviarComando("desbloquear");
    delay(300);
  }
}