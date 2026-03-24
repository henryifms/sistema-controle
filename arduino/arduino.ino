const int btn1 = 24;
const int btn2 = 26;

bool travadoTeclado = false;
bool travadoTela = false;

unsigned long lastPress1 = 0;
unsigned long lastPress2 = 0;
const int debounceDelay = 250;

void setup() {
  Serial.begin(9600);

  pinMode(btn1, INPUT_PULLUP);
  pinMode(btn2, INPUT_PULLUP);
}

void loop() {
  unsigned long agora = millis();

  if (digitalRead(btn1) == LOW && (agora - lastPress1 > debounceDelay)) {
    travadoTeclado = !travadoTeclado;

    if (travadoTeclado) {
      Serial.println("BLOQUEAR_TECLADO");
    } else {
      Serial.println("DESBLOQUEAR_TECLADO");
    }

    lastPress1 = agora;
  }

  if (digitalRead(btn2) == LOW && (agora - lastPress2 > debounceDelay)) {
    travadoTela = !travadoTela;

    if (travadoTela) {
      Serial.println("BLOQUEAR_TELA");
    } else {
      Serial.println("DESBLOQUEAR_TELA");
    }

    lastPress2 = agora;
  }
}
