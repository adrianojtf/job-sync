"""Textos dos e-mails transacionais de autenticação."""
from __future__ import annotations

_ASSINATURA = "\n\nEquipe job-sync"


def confirmacao_de_cadastro(link: str, horas_de_validade: int) -> tuple[str, str]:
    assunto = "Confirme seu e-mail no job-sync"
    corpo = (
        "Recebemos um cadastro no job-sync com este e-mail.\n\n"
        f"Para ativar sua conta, abra o link abaixo (vale por {horas_de_validade} horas):\n{link}\n\n"
        "Se não foi você, ignore esta mensagem. Nenhuma conta será ativada sem este link."
        + _ASSINATURA
    )
    return assunto, corpo


def conta_ja_existente(link_entrar: str, link_recuperar: str) -> tuple[str, str]:
    assunto = "Tentativa de cadastro no job-sync"
    corpo = (
        "Alguém tentou criar uma conta no job-sync com este e-mail, que já tem cadastro.\n\n"
        f"Para entrar: {link_entrar}\n"
        f"Se esqueceu a senha: {link_recuperar}\n\n"
        "Se não foi você, ignore esta mensagem. Sua conta não foi alterada."
        + _ASSINATURA
    )
    return assunto, corpo


def redefinicao_de_senha(link: str, minutos_de_validade: int) -> tuple[str, str]:
    assunto = "Redefinição de senha no job-sync"
    corpo = (
        "Recebemos um pedido para redefinir a senha da sua conta no job-sync.\n\n"
        f"Abra o link abaixo para escolher uma nova senha (vale por {minutos_de_validade} minutos):\n{link}\n\n"
        "Se não foi você, ignore esta mensagem. Sua senha atual continua valendo."
        + _ASSINATURA
    )
    return assunto, corpo
