"""Testes da entidade IdentidadeExterna."""

from uuid import uuid4

import pytest

from jobsync.autenticacao.domain.identidade_externa import IdentidadeExterna


class TestIdentidadeExterna:
    def test_cria_identidade_valida(self):
        usuario_id = uuid4()

        identidade = IdentidadeExterna(provedor="google", subject="1234", usuario_id=usuario_id)

        assert identidade.provedor == "google"
        assert identidade.subject == "1234"
        assert identidade.usuario_id == usuario_id

    @pytest.mark.parametrize("provedor,subject", [("", "1"), ("  ", "1"), ("google", ""), ("google", "  ")])
    def test_provedor_ou_subject_vazio_gera_erro(self, provedor, subject):
        with pytest.raises(ValueError):
            IdentidadeExterna(provedor=provedor, subject=subject, usuario_id=uuid4())
