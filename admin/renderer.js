const ipInput = document.getElementById('ip');
const connectBtn = document.getElementById('connect');

connectBtn.onclick = () => {
  window.api.conectar(ipInput.value, 5000);
};

function enviar(cmd) {
  window.api.enviar(cmd);
}
