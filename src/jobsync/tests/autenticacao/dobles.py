import re
from datetime import datetime, timedelta, timezone
from typing import Optional

INICIO = datetime(2026, 1, 10, 12, 0, tzinfo=timezone.utc)


class RelogioFalso:
    def __init__(self, inicio: datetime = INICIO) -> None:
        self.agora = inicio

    def __call__(self) -> datetime:
        return self.agora

    def avancar(self, **intervalo) -> None:
        self.agora = self.agora + timedelta(**intervalo)


class HasherSenhaFalso:
    def gerar(self, senha: str) -> str:
        return f"hash::{senha}"

    def conferir(self, senha: str, senha_hash: str) -> bool:
        return senha_hash == f"hash::{senha}"


class EnviadorEmailFalso:
    def __init__(self) -> None:
        self.enviados: list[tuple[str, str, str]] = []

    def enviar(self, para, assunto: str, corpo: str) -> None:
        self.enviados.append((para.valor, assunto, corpo))

    def para(self, email: str) -> list[tuple[str, str, str]]:
        return [envio for envio in self.enviados if envio[0] == email]

    def ultimo_token(self, email: str) -> Optional[str]:
        for _, _, corpo in reversed(self.para(email)):
            encontrado = re.search(r"token=([\w-]+)", corpo)
            if encontrado:
                return encontrado.group(1)
        return None
