import os
import sys

import pytest

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from app import create_app  # noqa: E402
from app.services.excel_service import cargar_excel  # noqa: E402
from config import Config, TestingConfig  # noqa: E402


@pytest.fixture(scope="session")
def repo():
    return cargar_excel(Config.DATA_PATH)


@pytest.fixture(scope="session")
def app():
    return create_app(TestingConfig)


@pytest.fixture()
def client(app):
    return app.test_client()
