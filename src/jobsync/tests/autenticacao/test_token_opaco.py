"""Testes das funções de token opaco."""

import hashlib

from jobsync.autenticacao.domain.token_opaco import chave_de_limite, gerar_token, hash_token


class TestTokenOpaco:
    def test_gera_tokens_diferentes_com_pelo_menos_43_caracteres(self):
        primeiro, segundo = gerar_token(), gerar_token()

        assert primeiro != segundo
        assert len(primeiro) >= 43

    def test_hash_e_sha256_do_token(self):
        assert hash_token("abc") == hashlib.sha256(b"abc").digest()

    def test_hash_e_deterministico(self):
        assert hash_token("abc") == hash_token("abc")

    def test_chave_de_limite_nao_expoe_o_valor(self):
        chave = chave_de_limite("email", "ana@exemplo.com")

        assert chave.startswith("email:")
        assert "ana@exemplo.com" not in chave

    def test_chaves_de_valores_diferentes_sao_diferentes(self):
        assert chave_de_limite("ip", "1.1.1.1") != chave_de_limite("ip", "2.2.2.2")
