// Service worker: orquestra a captura, buscando o texto da aba ativa via
// content.js e enviando para o ServidorCaptura local (job-sync), autenticado
// pelo token salvo em chrome.storage.local (configurado no popup).
const URL_SERVIDOR_CAPTURA = "http://localhost:8502/api/vagas/capturar";

async function capturarVagaDaAbaAtiva() {
  const [aba] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!aba || !aba.id) {
    throw new Error("Não foi possível identificar a aba ativa.");
  }

  const respostaConteudo = await chrome.tabs.sendMessage(aba.id, { tipo: "EXTRAIR_TEXTO_PAGINA" });
  if (!respostaConteudo || !respostaConteudo.texto) {
    throw new Error("Não foi possível extrair o texto da página.");
  }

  const { tokenCaptura } = await chrome.storage.local.get("tokenCaptura");
  if (!tokenCaptura) {
    throw new Error("Configure o token de captura no popup da extensão antes de capturar.");
  }

  const respostaServidor = await fetch(URL_SERVIDOR_CAPTURA, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${tokenCaptura}`,
    },
    body: JSON.stringify({ texto: respostaConteudo.texto, url: respostaConteudo.url }),
  });

  if (!respostaServidor.ok) {
    const detalhe = await respostaServidor.text();
    throw new Error(`Falha ao capturar vaga (status ${respostaServidor.status}): ${detalhe}`);
  }

  return respostaServidor.json();
}

chrome.runtime.onMessage.addListener((mensagem, remetente, enviarResposta) => {
  if (mensagem && mensagem.tipo === "CAPTURAR_VAGA") {
    capturarVagaDaAbaAtiva()
      .then((resultado) => enviarResposta({ sucesso: true, resultado }))
      .catch((erro) => enviarResposta({ sucesso: false, erro: erro.message }));
    return true;
  }
});
