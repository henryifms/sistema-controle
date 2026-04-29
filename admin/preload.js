const { contextBridge } = require('electron');
const net = require('net');

let client;

contextBridge.exposeInMainWorld('api', {
  conectar: (ip, porta) => {
    client = new net.Socket();
    client.connect(porta, ip, () => {
      console.log('Conectado ao servidor');
    });
  },

  enviar: (msg) => {
  console.log("ENVIANDO:", msg)
  if (client) {
    client.write(msg + "\n");
  } else {
    console.log("CLIENT NÃO EXISTE")
  }
}
});
