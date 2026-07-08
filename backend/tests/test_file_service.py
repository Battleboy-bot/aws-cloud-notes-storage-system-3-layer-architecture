import pytest

from app.middleware.exceptions import ValidationError
from app.services.file_service import FileService


class FakeRepository:
    def list(self, page, page_size):
        return [], 0

    def search_by_title(self, title, page, page_size):
        return [], 0


class FakeStorage:
    pass


@pytest.fixture
def service():
    return FileService(repository=FakeRepository(), storage=FakeStorage())


def test_list_files_returns_pagination(service):
    response = service.list_files(page=1, page_size=10)

    assert response["items"] == []
    assert response["pagination"] == {"page": 1, "page_size": 10, "total": 0}


def test_invalid_page_raises_validation_error(service):
    with pytest.raises(ValidationError):
        service.list_files(page=0, page_size=10)


def test_search_requires_title(service):
    with pytest.raises(ValidationError):
        service.search(title="", page=1, page_size=10)
