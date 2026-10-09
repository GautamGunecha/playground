from httpx import ASGITransport, AsyncClient

from app.main import create_app


async def test_health_endpoint_returns_ok() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_cors_allows_configured_origin(monkeypatch) -> None:
    monkeypatch.setenv(
        "PLAYGROUND_CORS_ORIGINS",
        "https://frontend.example, https://preview.example",
    )
    async with AsyncClient(
        transport=ASGITransport(app=create_app()),
        base_url="http://test",
    ) as client:
        response = await client.options(
            "/health",
            headers={
                "Origin": "https://frontend.example",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://frontend.example"


async def test_cors_rejects_unconfigured_origin() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=create_app(cors_origins=["https://frontend.example"])),
        base_url="http://test",
    ) as client:
        response = await client.options(
            "/health",
            headers={
                "Origin": "https://other.example",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert "access-control-allow-origin" not in response.headers
