"""Exceções do fluxo de leitura de dados de uma vaga a partir de link ou texto."""

from __future__ import annotations

from enum import Enum


class LinkVagaInvalido(ValueError):
    """O link informado não pode ser usado para identificar uma vaga."""


class FonteVagaNaoSuportada(Exception):
    """A fonte do link está desativada ou não é suportada."""


class MotivoLeituraIndisponivel(Enum):
    """Motivos pelos quais uma vaga não pôde ser lida a partir do link."""

    BLOQUEADA = "bloqueada"
    NAO_ENCONTRADA = "nao_encontrada"
    TEMPO_ESGOTADO = "tempo_esgotado"
    SEM_DADOS = "sem_dados"
    ENDERECO_RECUSADO = "endereco_recusado"
    FALHA_DE_REDE = "falha_de_rede"


_MENSAGENS_POR_MOTIVO = {
    MotivoLeituraIndisponivel.BLOQUEADA: (
        "O site não permitiu a leitura desta vaga. Cole o texto da vaga para continuar."
    ),
    MotivoLeituraIndisponivel.NAO_ENCONTRADA: (
        "A vaga não foi encontrada ou já foi encerrada. Confira o link ou cole o texto da vaga."
    ),
    MotivoLeituraIndisponivel.TEMPO_ESGOTADO: (
        "A leitura da vaga demorou mais que o esperado. Tente de novo ou cole o texto da vaga."
    ),
    MotivoLeituraIndisponivel.SEM_DADOS: (
        "Não foi possível encontrar os dados da vaga nesta página. Cole o texto da vaga para continuar."
    ),
    MotivoLeituraIndisponivel.ENDERECO_RECUSADO: (
        "Este endereço não pode ser lido. Use o link público da vaga ou cole o texto da vaga."
    ),
    MotivoLeituraIndisponivel.FALHA_DE_REDE: (
        "Não foi possível acessar o site da vaga agora. Tente de novo ou cole o texto da vaga."
    ),
}


class LeituraVagaIndisponivel(Exception):
    """A vaga não pôde ser lida; a mensagem orienta a pessoa a colar o texto."""

    def __init__(self, motivo: MotivoLeituraIndisponivel) -> None:
        super().__init__(_MENSAGENS_POR_MOTIVO[motivo])
        self.motivo = motivo


class LimiteLeituraVagaExcedido(Exception):
    """A pessoa atingiu o limite de leituras de vaga em um período."""

    def __init__(self, segundos_para_nova_tentativa: int) -> None:
        super().__init__("Limite de leituras de vaga atingido. Tente novamente mais tarde.")
        self.segundos_para_nova_tentativa = segundos_para_nova_tentativa
