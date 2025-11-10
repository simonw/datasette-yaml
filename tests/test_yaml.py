from datasette.app import Datasette
import pytest
import sqlite_utils
import textwrap


@pytest.mark.asyncio
async def test_plugin_is_installed():
    ds = Datasette([], memory=True)
    response = await ds.client.get("/-/plugins.json")
    assert response.status_code == 200
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
    ds = Datasette([str(db_path)])
    response = await ds.client.get("/test/dogs.yaml")
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
