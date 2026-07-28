const campoToken = document.getElementById("token");
const botaoSalvarToken = document.getElementById("salvarToken");
const botaoCapturar = document.getElementById("capturar");
const status = document.getElementById("status");

async function carregarToken() {
  const { tokenCaptura } = await chrome.storage.local.get("tokenCaptura");
  if (tokenCaptura) {
    campoToken.value = tokenCaptura;
  }
}

botaoSalvarToken.addEventListener("click", async () => {
  await chrome.storage.local.set({ tokenCaptura: campoToken.value.trim() });
  status.textContent = "Token salvo.";
  status.className = "sucesso";
});

botaoCapturar.addEventListener("click", () => {
  status.textContent = "Capturando...";
  status.className = "";
  chrome.runtime.sendMessage({ tipo: "CAPTURAR_VAGA" }, (resposta) => {
    if (resposta && resposta.sucesso) {
      status.textContent = "Vaga capturada com sucesso!";
      status.className = "sucesso";
    } else {
      status.textContent = `Erro: ${resposta ? resposta.erro : "desconhecido"}`;
      status.className = "erro";
    }
  });
});

carregarToken();
