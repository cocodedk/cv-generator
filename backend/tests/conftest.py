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


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API endpoint tests")


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver for testing."""
    mock_driver = Mock()
    mock_session = Mock()

    # Configure mock session
    mock_session.__enter__ = Mock(return_value=mock_session)
    mock_session.__exit__ = Mock(return_value=None)
    mock_session.run = Mock(return_value=Mock(single=Mock(return_value=None)))
    mock_session.execute_write = Mock(
        return_value=Mock(single=Mock(return_value={"cv_id": "test-cv-id"}))
    )
    mock_session.execute_read = Mock(return_value=Mock(single=Mock(return_value=None)))
    # Keep write_transaction and read_transaction for backwards compatibility in tests
    mock_session.write_transaction = mock_session.execute_write
    mock_session.read_transaction = mock_session.execute_read

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
                "description": "Led a small team delivering product features.",
                "location": "Remote",
                "projects": [
                    {
                        "name": "Internal Platform",
                        "description": "Unified services into a single developer platform.",
                        "technologies": ["FastAPI", "PostgreSQL", "React"],
                        "highlights": [
                            "Reduced onboarding time by standardizing templates and tooling.",
                            "Improved reliability with automated health checks and alerting.",
                        ],
                        "url": "https://example.com/platform",
                    }
                ],
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
    Neo4jConnection.reset()
    yield
    Neo4jConnection.reset()


@pytest.fixture(scope="module")
def pdf_service():
    """PDF service instance for integration tests."""
    from backend.services.pdf_service import PDFService

    return PDFService(timeout=30)  # Shorter timeout for tests


@pytest.fixture
def sample_html_content():
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
            h1 { margin: 0 0 20px 0; }
            p { margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>Test CV</h1>
        <p>This is a test CV content.</p>
    </body>
    </html>
    """


@pytest.fixture
def long_html_content():
    """Long HTML content for testing (> 5000px height)."""
    parts = [
        """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { margin: 0; padding: 20px; font-family: Arial, sans-serif; }
            .section { margin: 50px 0; min-height: 500px; }
        </style>
    </head>
    <body>
    """
    ]
    # Add many sections to create long content
    for i in range(15):
        parts.append(
            f'<div class="section"><h2>Section {i+1}</h2><p>Content for section {i+1}</p></div>'
        )
    parts.append(
        """
    </body>
    </html>
    """
    )
    return "".join(parts)
