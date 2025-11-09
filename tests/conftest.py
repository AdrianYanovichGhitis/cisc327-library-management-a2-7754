import pytest
import os

from database import init_database, add_sample_data


@pytest.fixture(scope="session", autouse=True)
def init_db():
    """Initialize the SQLite database and seed sample data for tests."""
    # Ensure database exists and has tables/sample data
    init_database()
    add_sample_data()
    yield
    # Teardown: remove the database file to avoid state leakage
    try:
        os.remove('library.db')
    except Exception:
        pass
