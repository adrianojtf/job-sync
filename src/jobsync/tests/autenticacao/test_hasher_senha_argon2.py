"""Testes do HasherSenhaArgon2."""

from jobsync.autenticacao.adapters.hasher_senha_argon2 import HasherSenhaArgon2


class TestHasherSenhaArgon2:
    def test_gera_hash_argon2id(self):
        hash_ = HasherSenhaArgon2().gerar("uma-senha-longa")

        assert hash_.startswith("$argon2id$")
        assert "uma-senha-longa" not in hash_

    def test_confere_senha_correta(self):
        hasher = HasherSenhaArgon2()
        hash_ = hasher.gerar("uma-senha-longa")

        assert hasher.conferir("uma-senha-longa", hash_) is True

    def test_rejeita_senha_incorreta(self):
        hasher = HasherSenhaArgon2()
        hash_ = hasher.gerar("uma-senha-longa")

        assert hasher.conferir("outra-senha-longa", hash_) is False

    def test_hash_malformado_devolve_falso_sem_levantar_erro(self):
        assert HasherSenhaArgon2().conferir("qualquer", "isto-nao-e-um-hash") is False

    def test_mesma_senha_gera_hashes_diferentes(self):
        hasher = HasherSenhaArgon2()

        assert hasher.gerar("uma-senha-longa") != hasher.gerar("uma-senha-longa")
