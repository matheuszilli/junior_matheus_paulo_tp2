import secrets

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from routes import autenticacao, health, predicao
from security.rate_limit import limiter


app = FastAPI(
    title="Sistema de Atendimento ao Cliente",
    docs_url=None,
    redoc_url=None,
)


app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=[
        "Authorization",
        "Content-Type",
    ],
)


@app.middleware("http")
async def adicionar_headers_seguranca(
        request: Request,
        call_next,
):
    response = await call_next(request)

    response.headers[
        "Strict-Transport-Security"
    ] = "max-age=31536000; includeSubDomains"

    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    response.headers[
        "Referrer-Policy"
    ] = "no-referrer"

    response.headers[
        "Permissions-Policy"
    ] = "camera=(), microphone=(), geolocation=()"

    response.headers[
        "Cross-Origin-Opener-Policy"
    ] = "same-origin"

    response.headers[
        "Cross-Origin-Resource-Policy"
    ] = "same-origin"

    response.headers[
        "Cross-Origin-Embedder-Policy"
    ] = "require-corp"

    response.headers[
        "Cache-Control"
    ] = "no-store"

    response.headers[
        "Pragma"
    ] = "no-cache"

    response.headers[
        "Content-Security-Policy"
    ] = response.headers.get(
        "Content-Security-Policy",
        "default-src 'none'; "
        "frame-ancestors 'none'; "
        "base-uri 'none'; "
        "form-action 'none'; "
        "object-src 'none'",
    )

    return response


@app.get("/docs", include_in_schema=False, response_class=HTMLResponse)
def documentacao():
    nonce = secrets.token_urlsafe(24)
    versao_swagger = "5.33.1"
    integridade_script = (
        "sha384-ZPehFMQommnnuaZ4rpxgkgTT2DKFVp4hZC/7pLit+9Lek9T1YGSo23eHFbvNkX"
    )
    integridade_estilo = (
        "sha384-Ov4/wv3j2bmct8cDc5X4ngJZohVPzEmc6uDPH8WeljUxO5vtoykvMEfbu9Vh6RaW"
    )

    conteudo = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Documentação da API</title>
    <link rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@{versao_swagger}/swagger-ui.css"
          integrity="{integridade_estilo}"
          crossorigin="anonymous">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@{versao_swagger}/swagger-ui-bundle.js"
            integrity="{integridade_script}"
            crossorigin="anonymous"></script>
    <script nonce="{nonce}">
        SwaggerUIBundle({{
            url: "/openapi.json",
            dom_id: "#swagger-ui",
            deepLinking: true,
            layout: "BaseLayout"
        }});
    </script>
</body>
</html>"""

    response = HTMLResponse(conteudo)
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; "
        f"script-src https://cdn.jsdelivr.net 'nonce-{nonce}'; "
        "style-src https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'none'; "
        "form-action 'none'; "
        "object-src 'none'"
    )
    return response


app.include_router(health.router)
app.include_router(autenticacao.router)
app.include_router(predicao.router)
