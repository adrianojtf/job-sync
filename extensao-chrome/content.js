// Extrai o texto principal da página quando solicitado pelo background/popup.
// Heurística genérica (document.body.innerText) — sem seletores específicos
// por site, para não depender de manutenção contínua a cada mudança de
// layout de sites de vagas (LinkedIn, Gupy, etc).
chrome.runtime.onMessage.addListener((mensagem, remetente, enviarResposta) => {
  if (mensagem && mensagem.tipo === "EXTRAIR_TEXTO_PAGINA") {
    const texto = document.body ? document.body.innerText : "";
    enviarResposta({ texto, url: window.location.href });
  }
  return true;
});
