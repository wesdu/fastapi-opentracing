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