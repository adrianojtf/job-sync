import hashlib
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import psycopg
import pytest

from jobsync.tests.shared_kernel.banco_sqlite_antigo import DADOS, PDF_A, SCHEMA_ANTIGO, criar_sqlite
from jobsync.shared_kernel.adapters.persistence.migracao_sqlite import (
    DestinoInvalido,
    OrigemInvalida,
    ValidacaoFalhou,
    converter_data,
    hash_pdf,
    migrar,
)

@pytest.fixture
def sqlite_origem(tmp_path):
    caminho = tmp_path / "job_sync.db"
    criar_sqlite(caminho)
    return caminho


@pytest.fixture
def destino(url_banco_teste, pool_postgres):
    with psycopg.connect(url_banco_teste, options="-c TimeZone=UTC") as conexao:
        yield conexao


def _contagem(pool, tabela: str) -> int:
    with pool.connection() as conexao:
        return conexao.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]


def _hash_arquivo(caminho) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


SAO_PAULO = ZoneInfo("America/Sao_Paulo")


class TestConverterData:
    def test_data_sem_fuso_e_interpretada_no_fuso_informado(self):
        resultado = converter_data("2026-03-10T09:30:00", SAO_PAULO)

        assert resultado == datetime(2026, 3, 10, 12, 30, tzinfo=timezone.utc)
        assert resultado.utcoffset() == timedelta(0)

    def test_data_com_fuso_e_normalizada_para_utc(self):
        resultado = converter_data("2026-03-10T09:30:00+02:00", None)

        assert resultado == datetime(2026, 3, 10, 7, 30, tzinfo=timezone.utc)

    def test_data_invalida_levanta_value_error(self):
        with pytest.raises(ValueError):
            converter_data("ontem", None)


class TestHashPdf:
    def test_e_o_sha256_do_conteudo(self):
        assert hash_pdf(b"abc") == hashlib.sha256(b"abc").hexdigest()


class TestMigrar:
    def test_copia_todas_as_tabelas_e_relata_contagens(self, sqlite_origem, destino, pool_postgres):
        relatorio = migrar(sqlite_origem, destino, fuso_origem=SAO_PAULO)

        assert {l.tabela: (l.lidos, l.gravados) for l in relatorio.linhas} == {
            "perfil": (2, 2),
            "curriculo_salvo": (2, 2),
            "token_captura": (1, 1),
            "vaga": (2, 2),
            "candidatura": (3, 3),
            "perfil_estruturado": (1, 1),
        }
        assert relatorio.pdfs_conferidos == 2
        assert _contagem(pool_postgres, "candidatura") == 3

    def test_preserva_pdf_binario_ordem_do_board_e_booleano(self, sqlite_origem, destino, pool_postgres):
        migrar(sqlite_origem, destino, fuso_origem=SAO_PAULO)

        with pool_postgres.connection() as conexao:
            pdf = conexao.execute("SELECT pdf_bytes FROM curriculo_salvo WHERE id = 'cs1'").fetchone()[0]
            posicoes = dict(conexao.execute("SELECT id, posicao FROM candidatura").fetchall())
            convertidas = dict(conexao.execute("SELECT id, convertida_em_candidatura FROM vaga").fetchall())
        assert bytes(pdf) == PDF_A
        assert posicoes == {"c1": 1, "c2": 0, "c3": 0}
        assert convertidas == {"v1": True, "v2": False}

    def test_converte_datas_para_utc_usando_o_fuso_de_origem(self, sqlite_origem, destino, pool_postgres):
        migrar(sqlite_origem, destino, fuso_origem=SAO_PAULO)

        with pool_postgres.connection() as conexao:
            captura = conexao.execute("SELECT data_captura FROM vaga WHERE id = 'v1'").fetchone()[0]
        assert captura == datetime(2026, 3, 10, 12, 30, tzinfo=timezone.utc)

    def test_perfil_estruturado_vira_jsonb(self, sqlite_origem, destino, pool_postgres):
        migrar(sqlite_origem, destino, fuso_origem=SAO_PAULO)

        with pool_postgres.connection() as conexao:
            experiencias, tecnologias = conexao.execute(
                "SELECT experiencias_json, tecnologias_json FROM perfil_estruturado"
            ).fetchone()
        assert experiencias == [{"empresa": "Acme", "cargo": "Dev"}]
        assert tecnologias == ["Python", "SQL"]

    def test_nao_altera_o_arquivo_sqlite(self, sqlite_origem, destino):
        antes = _hash_arquivo(sqlite_origem)

        migrar(sqlite_origem, destino, fuso_origem=SAO_PAULO)

        assert _hash_arquivo(sqlite_origem) == antes

    def test_simulacao_valida_mas_nao_grava(self, sqlite_origem, destino, pool_postgres):
        relatorio = migrar(sqlite_origem, destino, simulacao=True, fuso_origem=SAO_PAULO)

        assert relatorio.simulacao is True
        assert relatorio.linhas[4].gravados == 3
        assert _contagem(pool_postgres, "candidatura") == 0
        assert _contagem(pool_postgres, "perfil") == 0

    def test_segunda_execucao_e_recusada_sem_duplicar(self, sqlite_origem, destino, pool_postgres):
        migrar(sqlite_origem, destino, fuso_origem=SAO_PAULO)

        with pytest.raises(DestinoInvalido, match="perfil"):
            migrar(sqlite_origem, destino, fuso_origem=SAO_PAULO)

        assert _contagem(pool_postgres, "perfil") == 2

    def test_falha_na_validacao_desfaz_tudo(self, sqlite_origem, destino, pool_postgres, monkeypatch):
        def divergir(*_args, **_kwargs):
            raise ValidacaoFalhou(["divergência induzida"])

        monkeypatch.setattr("jobsync.shared_kernel.adapters.persistence.migracao_sqlite._validar", divergir)

        with pytest.raises(ValidacaoFalhou):
            migrar(sqlite_origem, destino, fuso_origem=SAO_PAULO)

        assert _contagem(pool_postgres, "perfil") == 0
        assert _contagem(pool_postgres, "curriculo_salvo") == 0


class TestCurriculoRemovidoEmUso:
    @pytest.fixture
    def sqlite_com_curriculo_removido(self, tmp_path):
        caminho = tmp_path / "orfao.db"
        criar_sqlite(
            caminho,
            extra="""
            INSERT INTO candidatura VALUES
              ('c4', 'ana', NULL, 'removido-1', 'Delta', 'Dev', 'APLICADO',
               '2026-03-15T10:00:00', '2026-03-15T10:00:00', 2);
            """,
        )
        return caminho

    def test_candidatura_com_curriculo_removido_e_migrada_com_aviso(
        self, sqlite_com_curriculo_removido, destino, pool_postgres
    ):
        relatorio = migrar(sqlite_com_curriculo_removido, destino, fuso_origem=SAO_PAULO)

        with pool_postgres.connection() as conexao:
            curriculo = conexao.execute("SELECT curriculo_salvo_id FROM candidatura WHERE id = 'c4'").fetchone()[0]
        assert curriculo == "removido-1"
        assert _contagem(pool_postgres, "candidatura") == 4
        assert len(relatorio.avisos) == 1
        assert "c4" in relatorio.avisos[0]
        assert "removido-1" in relatorio.avisos[0]

    def test_origem_sem_orfaos_nao_gera_avisos(self, sqlite_origem, destino):
        relatorio = migrar(sqlite_origem, destino, fuso_origem=SAO_PAULO)

        assert relatorio.avisos == ()

    def test_vaga_inexistente_continua_sendo_problema(self, tmp_path, destino):
        caminho = tmp_path / "vaga-orfa.db"
        criar_sqlite(
            caminho,
            extra="""
            INSERT INTO candidatura VALUES
              ('c5', 'ana', 'vaga-fantasma', NULL, 'Eps', 'Dev', 'APLICADO',
               '2026-03-15T10:00:00', '2026-03-15T10:00:00', 3);
            """,
        )

        with pytest.raises(OrigemInvalida, match="aponta para vaga inexistente"):
            migrar(caminho, destino, fuso_origem=SAO_PAULO)


class TestOrigemInvalida:
    def test_referencia_orfa_data_e_json_invalidos_sao_relatados_juntos(self, tmp_path, destino, pool_postgres):
        caminho = tmp_path / "ruim.db"
        criar_sqlite(
            caminho,
            extra="""
            INSERT INTO vaga VALUES ('v3', 'fantasma', 'Orfa', NULL, '2026-03-11T10:00:00', 0);
            INSERT INTO vaga VALUES ('v4', 'ana', 'Data ruim', NULL, 'ontem', 0);
            UPDATE perfil_estruturado SET tecnologias_json = 'nao-e-json';
            """,
        )

        with pytest.raises(OrigemInvalida) as erro:
            migrar(caminho, destino, fuso_origem=SAO_PAULO)

        texto = " | ".join(erro.value.problemas)
        assert "órfã" in texto
        assert "Data inválida em vaga.data_captura" in texto
        assert "JSON inválido em perfil_estruturado.tecnologias_json" in texto
        assert _contagem(pool_postgres, "perfil") == 0

    def test_banco_antigo_sem_posicao_e_recusado_com_orientacao(self, tmp_path, destino):
        caminho = tmp_path / "antigo.db"
        schema = SCHEMA_ANTIGO.replace(",\n    posicao INTEGER NOT NULL DEFAULT 0", "")
        criar_sqlite(caminho, dados="INSERT INTO perfil VALUES ('ana');", schema=schema)

        with pytest.raises(OrigemInvalida, match="versão anterior"):
            migrar(caminho, destino)

    def test_arquivo_inexistente_e_recusado(self, tmp_path, destino):
        with pytest.raises(OrigemInvalida, match="não encontrado"):
            migrar(tmp_path / "nao-existe.db", destino)
