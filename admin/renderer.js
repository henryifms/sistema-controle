const ipInput = document.getElementById('ip');
const portaInput = document.getElementById('porta');
const connectBtn = document.getElementById('connect');
const salaSelect = document.getElementById('sala');
const statusDiv = document.getElementById('status');

const btnTeclado = document.getElementById('btnTeclado');
const btnTela = document.getElementById('btnTela');

let tecladoBloqueado = false;
let telaBloqueada = false;
let timerTeclado = null;
let timerTela = null;

// Conecta ao servidor
connectBtn.onclick = () => {
  const host = ipInput.value;
  const port = parseInt(portaInput.value) || 80;
  
  console.log(`Conectando a ${host}:${port}...`);
  window.api.conectar(host, port);
};

// Atualiza status visual
window.api.onStatus((data) => {
  if (data.connected) {
    statusDiv.textContent = `Conectado a ${data.host}:${data.port}`;
    statusDiv.className = 'status connected';
  } else {
    statusDiv.textContent = 'Desconectado';
    statusDiv.className = 'status disconnected';
  }
});

// Função de envio
function enviar(cmd) {
  const sala = salaSelect.value;
  const mensagem = `${sala}:${cmd}`;
  console.log("ENVIANDO:", mensagem);
  window.api.enviar(mensagem);
}

// TECLADO
btnTeclado.onclick = () => {
  tecladoBloqueado = !tecladoBloqueado;
  if (timerTeclado) clearTimeout(timerTeclado);

  if (tecladoBloqueado) {
    enviar("BLOQUEAR_TECLADO");
    btnTeclado.textContent = "Teclado Bloqueado";
    btnTeclado.className = "on";
    
    timerTeclado = setTimeout(() => {
      enviar("DESBLOQUEAR_TECLADO");
      tecladoBloqueado = false;
      btnTeclado.textContent = "Teclado Livre";
      btnTeclado.className = "off";
    }, 10000);
  } else {
    enviar("DESBLOQUEAR_TECLADO");
    btnTeclado.textContent = "Teclado Livre";
    btnTeclado.className = "off";
  }
};

// TELA
btnTela.onclick = () => {
  telaBloqueada = !telaBloqueada;
  if (timerTela) clearTimeout(timerTela);

  if (telaBloqueada) {
    enviar("BLOQUEAR_TELA");
    btnTela.textContent = "Tela Bloqueada";
    btnTela.className = "on";
    
    timerTela = setTimeout(() => {
      enviar("DESBLOQUEAR_TELA");
      telaBloqueada = false;
      btnTela.textContent = "Tela Livre";
      btnTela.className = "off";
    }, 10000);
  } else {
    enviar("DESBLOQUEAR_TELA");
    btnTela.textContent = "Tela Livre";
    btnTela.className = "off";
  }
};
