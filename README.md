# fastapi-opentracing
fastapi opentracing middleware works with istio

install:

```
pip install fastapi-opentracing
```
   
example:

```python
from fastapi import FastAPI
import uvicorn
from fastapi_opentracing import get_opentracing_span_headers
from fastapi_opentracing.middleware import OpenTracingMiddleware

app = FastAPI()

app.add_middleware(OpenTracingMiddleware)


@app.get("/")
async def root():
    carrier = await get_opentracing_span_headers()
    return {'span': carrier}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

if your application uses tortoise-orm, you can specify the client 
`mysql_client.install_patch` to patch you SQLClient

example:

```python
from fastapi import FastAPI
import uvicorn
from fastapi_opentracing import get_opentracing_span_headers
from fastapi_opentracing.middleware import OpenTracingMiddleware
from fastapi_opentracing.client_hooks.mysql_client import install_patch
from fastapi_opentracing.client_hooks import install_all_patch


app = FastAPI()

app.add_middleware(OpenTracingMiddleware)
TORTOISE_ORM = {
    "connections": {"default": "mysql://root:123456@127.0.0.1:3306/test"},
    "apps": {
        "models": {
            "models": ["tests.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True
)

install_all_patch()

@app.get("/")
async def root():
    carrier = await get_opentracing_span_headers()
    return {'span': carrier}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```


Contributing and Developing

To install all dependencies, run:
```shell
python3 -m venv venv
source venv/bin/activate
make bootstrap
```

Running Tests
```shell
make test
```

Check the style and quality of python code
```shell
make lint
```

