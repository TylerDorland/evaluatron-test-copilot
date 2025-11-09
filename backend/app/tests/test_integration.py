import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.models import Company, User, Topic
from app.core.security import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_company():
    db = TestingSessionLocal()
    company = Company(name="Integration Test Company", is_active=True)
    db.add(company)
    db.commit()
    db.refresh(company)
    db.close()
    return company


@pytest.fixture
def test_user(test_company):
    db = TestingSessionLocal()
    user = User(
        email="integration@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Integration User",
        company_id=test_company.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user


@pytest.fixture
def auth_token(test_user):
    response = client.post(
        "/api/auth/login",
        data={"username": "integration@example.com", "password": "password123"}
    )
    return response.json()["access_token"]


def test_complete_workflow(auth_token, test_company):
    """Test complete workflow: create topic, create query, run evaluation"""
    
    # Step 1: Create a topic
    topic_response = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Test Topic",
            "description": "Integration test topic",
            "company_id": test_company.id
        }
    )
    assert topic_response.status_code == 200
    topic_id = topic_response.json()["id"]
    
    # Step 2: Create an LLM query (will fail without real API keys, but that's ok)
    query_response = client.post(
        "/api/queries/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "prompt": "What is the meaning of life?",
            "llm_provider": "openai",
            "model_name": "gpt-3.5-turbo",
            "topic_id": topic_id
        }
    )
    assert query_response.status_code == 200
    query_data = query_response.json()
    query_id = query_data["id"]
    
    # The query will fail without real API keys, but let's check it was created
    assert query_data["prompt"] == "What is the meaning of life?"
    assert query_data["llm_provider"] == "openai"
    
    # Step 3: List queries
    queries_response = client.get(
        "/api/queries/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert queries_response.status_code == 200
    queries = queries_response.json()
    assert len(queries) == 1
    assert queries[0]["id"] == query_id
    
    # Step 4: Get specific query
    query_detail_response = client.get(
        f"/api/queries/{query_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert query_detail_response.status_code == 200
    assert query_detail_response.json()["id"] == query_id


def test_multi_tenant_isolation(test_company, test_user):
    """Test that users can only access their company's data"""
    
    # Create second company and user
    db = TestingSessionLocal()
    company2 = Company(name="Another Company", is_active=True)
    db.add(company2)
    db.commit()
    db.refresh(company2)
    
    user2 = User(
        email="user2@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="User 2",
        company_id=company2.id,
        is_active=True
    )
    db.add(user2)
    db.commit()
    db.close()
    
    # Login as first user
    response1 = client.post(
        "/api/auth/login",
        data={"username": "integration@example.com", "password": "password123"}
    )
    token1 = response1.json()["access_token"]
    
    # Login as second user
    response2 = client.post(
        "/api/auth/login",
        data={"username": "user2@example.com", "password": "password123"}
    )
    token2 = response2.json()["access_token"]
    
    # Create topic as user1
    topic_response = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "name": "User1 Topic",
            "description": "Topic for user 1",
            "company_id": test_company.id
        }
    )
    assert topic_response.status_code == 200
    topic_id = topic_response.json()["id"]
    
    # User2 should not be able to access User1's topic
    topic_get_response = client.get(
        f"/api/topics/{topic_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert topic_get_response.status_code == 403
    
    # User1 should be able to access their own topic
    topic_get_response = client.get(
        f"/api/topics/{topic_id}",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert topic_get_response.status_code == 200


def test_scheduled_test_lifecycle(auth_token, test_company):
    """Test creating and managing scheduled tests"""
    
    # Create topic first
    topic_response = client.post(
        "/api/topics/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Scheduled Test Topic",
            "description": "Topic for scheduled tests",
            "company_id": test_company.id
        }
    )
    topic_id = topic_response.json()["id"]
    
    # Create scheduled test
    test_response = client.post(
        "/api/scheduled-tests/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "name": "Daily Test",
            "prompt_template": "Test prompt",
            "llm_providers": ["openai", "anthropic"],
            "topic_id": topic_id,
            "cron_expression": "0 9 * * *",
            "evaluation_types": ["sentiment", "clarity"]
        }
    )
    assert test_response.status_code == 200
    test_data = test_response.json()
    test_id = test_data["id"]
    assert test_data["is_active"] is True
    
    # Toggle test status
    update_response = client.put(
        f"/api/scheduled-tests/{test_id}?is_active=false",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["is_active"] is False
