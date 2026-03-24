const int led = 22;
const int btn1 = 24;
const int btn2 = 26;

// Estados e controle de tempo
bool travadoTeclado = false;
bool travadoTela = false;
unsigned long lastPress1 = 0;
unsigned long lastPress2 = 0;
const int debounceDelay = 250;

// Configuração do Pisca Rápido
int piscasRestantes = 0;      // Contador de piscadas
unsigned long lastPisco = 0;  // Tempo da última alternância do LED
const int intervaloPisca = 70; // Velocidade (70ms é bem rápido)

void setup() {
  Serial.begin(9600);
  pinMode(btn1, INPUT_PULLUP);
  pinMode(btn2, INPUT_PULLUP);
  pinMode(led, OUTPUT);
  digitalWrite(led, LOW);
}

void loop() {
  unsigned long agora = millis();

  // 1. Receber dados da Serial
  if (Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg == "CLIENTE_CONECTADO") {
      piscasRestantes = 5;
    }
  }

  if (piscasRestantes > 0) {
    if (agora - lastPisco >= intervaloPisca) {
      lastPisco = agora;
      piscasRestantes--;
      
      
      digitalWrite(led, !digitalRead(led));
      
    
      if (piscasRestantes == 0) {
        digitalWrite(led, LOW);
      }
    }
  }

  if (digitalRead(btn1) == LOW && (agora - lastPress1 > debounceDelay)) {
    travadoTeclado = !travadoTeclado;
    Serial.println(travadoTeclado ? "BLOQUEAR_TECLADO" : "DESBLOQUEAR_TECLADO");
    lastPress1 = agora;
  }

  // 4. Botão 2 - Tela
  if (digitalRead(btn2) == LOW && (agora - lastPress2 > debounceDelay)) {
    travadoTela = !travadoTela;
    Serial.println(travadoTela ? "BLOQUEAR_TELA" : "DESBLOQUEAR_TELA");
    lastPress2 = agora;
  }
}
