import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.database import Base, get_db
from backend.main import app

@pytest.fixture(scope="function")
def client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_trades_empty(client):
    res = client.get("/trades/")
    assert res.status_code == 200
    assert res.json() == []


def test_analytics_overview_empty(client):
    res = client.get("/analytics/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["win_rate"] == 0
    assert data["total_pnl"] == 0


def test_campaigns_create_and_list(client):
    res = client.post("/campaigns/", json={"name": "TSLA Wheel", "symbol": "TSLA"})
    assert res.status_code == 200
    data = res.json()
    assert data["symbol"] == "TSLA"
    assert data["status"] == "active"

    res2 = client.get("/campaigns/")
    assert res2.status_code == 200
    assert len(res2.json()) == 1


def test_campaign_complete(client):
    res = client.post("/campaigns/", json={"name": "AAPL Wheel", "symbol": "AAPL"})
    cid = res.json()["id"]
    res2 = client.patch(f"/campaigns/{cid}/complete")
    assert res2.status_code == 200
    campaigns = client.get("/campaigns/").json()
    assert campaigns[0]["status"] == "completed"
