from pathlib import Path

from fastapi.testclient import TestClient

from jobsync.entrypoints.api.main import app


class TestSegurancaDependencias:
    def test_nenhuma_operacao_expoe_caminho_banco(self):
        parametros = [
            (rota, metodo, parametro["name"])
            for rota, operacoes in app.openapi()["paths"].items()
            for metodo, operacao in operacoes.items()
            for parametro in operacao.get("parameters", [])
        ]

        assert [p for p in parametros if p[2] == "caminho_banco"] == []

    def test_query_caminho_banco_e_ignorada(self, tmp_path: Path):
        banco_injetado = tmp_path / "injetado.db"

        response = TestClient(app).get(
            "/v1/vagas",
            params={"perfil_identificador": "adriano", "caminho_banco": str(banco_injetado)},
        )

        assert response.status_code == 200
        assert not banco_injetado.exists()
