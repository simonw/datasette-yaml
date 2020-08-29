from datasette import hookimpl
from datasette.utils.asgi import Response
from yaml import dump


def render_yaml(rows):
    return Response.text(dump([dict(r) for r in rows], sort_keys=False))


@hookimpl
def register_output_renderer():
    return {"extension": "yaml", "render": render_yaml}
