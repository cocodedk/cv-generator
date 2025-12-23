"""Pytest fixtures and configuration."""
import pytest
import pytest_asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch
from httpx import AsyncClient
from backend.app import app
from backend.database.connection import Neo4jConnection


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver for testing."""
    mock_driver = Mock()
    mock_session = Mock()
    mock_transaction = Mock()

    # Configure mock session
    mock_session.__enter__ = Mock(return_value=mock_session)
    mock_session.__exit__ = Mock(return_value=None)
    mock_session.run = Mock(return_value=Mock(single=Mock(return_value=None)))
    mock_session.write_transaction = Mock(
        return_value=Mock(single=Mock(return_value={"cv_id": "test-cv-id"}))
    )

    # Configure mock driver
    mock_driver.session = Mock(return_value=mock_session)
    mock_driver.verify_connectivity = Mock(return_value=True)
    mock_driver.close = Mock()

    return mock_driver


@pytest.fixture
def mock_neo4j_connection(mock_neo4j_driver):
    """Mock Neo4j connection."""
    with patch.object(Neo4jConnection, "get_driver", return_value=mock_neo4j_driver):
        with patch.object(Neo4jConnection, "get_database", return_value="neo4j"):
            with patch.object(
                Neo4jConnection, "verify_connectivity", return_value=True
            ):
                yield mock_neo4j_driver


@pytest_asyncio.fixture
async def client():
    """FastAPI test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_cv_data() -> Dict[str, Any]:
    """Sample CV data for testing."""
    return {
        "personal_info": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "USA",
            },
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "summary": "Experienced software developer",
        },
        "experience": [
            {
                "title": "Senior Developer",
                "company": "Tech Corp",
                "start_date": "2020-01",
                "end_date": "2023-12",
                "description": "Led development team",
                "location": "Remote",
            }
        ],
        "education": [
            {
                "degree": "BS Computer Science",
                "institution": "University of Technology",
                "year": "2018",
                "field": "Computer Science",
                "gpa": "3.8",
            }
        ],
        "skills": [
            {"name": "Python", "category": "Programming", "level": "Expert"},
            {"name": "React", "category": "Frontend", "level": "Advanced"},
        ],
        "theme": "classic",
    }


@pytest.fixture
def temp_output_dir():
    """Temporary directory for test file output."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture(autouse=True)
def reset_neo4j_connection():
    """Reset Neo4j connection state before each test."""
    Neo4jConnection._driver = None
    Neo4jConnection._database = None
    yield
    Neo4jConnection._driver = None
    Neo4jConnection._database = None
