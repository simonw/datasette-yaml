from datasette.app import Datasette
import httpx
import pytest
import sqlite_utils
import textwrap


@pytest.mark.asyncio
async def test_plugin_is_installed():
    app = Datasette([], memory=True).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/-/plugins.json")
        assert 200 == response.status_code
        installed_plugins = {p["name"] for p in response.json()}
        assert "datasette-yaml" in installed_plugins


@pytest.mark.asyncio
async def test_datasette_yaml(tmp_path_factory):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test.db"
    db = sqlite_utils.Database(db_path)
    db["dogs"].insert_all(
        [
            {"id": 1, "name": "Cleo", "age": 5, "weight": 48.4},
            {"id": 2, "name": "Pancakes", "age": 4, "weight": 33.2},
        ],
        pk="id",
    )
    app = Datasette([str(db_path)]).app()
    async with httpx.AsyncClient(app=app) as client:
        response = await client.get("http://localhost/test/dogs.yaml")
        assert response.status_code == 200
        assert (
            response.text.strip()
            == textwrap.dedent(
                """
        - id: 1
          name: Cleo
          age: 5
          weight: 48.4
        - id: 2
          name: Pancakes
          age: 4
          weight: 33.2
        """
            ).strip()
        )
