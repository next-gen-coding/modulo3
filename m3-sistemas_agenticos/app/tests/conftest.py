import os
import pytest

# URLs de la API y frontend, configurables por variables de entorno
URL_API = os.getenv("URL_API", "http://localhost:8000")
URL_WEB = os.getenv("URL_WEB", "http://localhost:8080")


@pytest.fixture
def url_api():
    """URL base de la API."""
    return URL_API


@pytest.fixture
def url_web():
    """URL base del frontend."""
    return URL_WEB
