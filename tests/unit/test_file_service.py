# tests/unit/test_file_service.py
#
# Pure unit tests for UploadedFileService with mocked UploadedFileDAO.
# WHY: Validates file metadata tracking for posters and documents.

import pytest
from unittest.mock import MagicMock
from Services.uploaded_file_service import UploadedFileService
from models.uploaded_file import UploadedFile


@pytest.mark.unit
class TestFileService:
    @pytest.fixture(autouse=True)
    def setup_service(self):
        self.file_service = UploadedFileService()
        self.mock_dao = MagicMock()
        self.file_service.file_dao = self.mock_dao

    def test_create_file_record(self):
        """WHY: Saving file metadata validates required filenames and paths."""
        fake_f = UploadedFile(id=1, user_id=2, original_filename="passport.pdf", stored_filename="hash.pdf", file_path="uploads/hash.pdf")
        self.mock_dao.create_file.return_value = fake_f

        res = self.file_service.create_file({
            "user_id": 2, "original_filename": "passport.pdf", "stored_filename": "hash.pdf", "file_path": "uploads/hash.pdf"
        })
        assert res["success"] is True
        assert res["data"]["original_filename"] == "passport.pdf"

    def test_get_file_by_id_missing(self):
        """WHY: Non-existent file ID returns 404."""
        self.mock_dao.get_file_by_id.return_value = None
        res = self.file_service.get_file_by_id(999)
        assert res["success"] is False
        assert res["status"] == 404
