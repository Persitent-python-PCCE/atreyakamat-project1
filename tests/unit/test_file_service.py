# tests/unit/test_file_service.py
#
# WHY: Unit tests for local event poster image uploads, validation rules,
# file paths, size limits, and physical file operations.
# Uses temporary directories to prevent cluttering local project space.

import os
import pytest
from io import BytesIO
from unittest.mock import MagicMock, patch
from werkzeug.datastructures import FileStorage
from Services.uploaded_file_service import UploadedFileService
from models.uploaded_file import UploadedFile


@pytest.mark.unit
class TestFileServiceUploads:
    @pytest.fixture(autouse=True)
    def setup_service(self, tmp_path):
        # WHY: We run tests against a temporary directory so we don't write to the real uploads directory
        self.upload_dir = tmp_path / "static" / "uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.file_service = UploadedFileService()
        self.mock_dao = MagicMock()
        self.file_service.file_dao = self.mock_dao

    @patch("flask.current_app")
    def test_save_poster_valid(self, mock_app):
        """WHY: Valid image file stores successfully and returns 201 with stored path."""
        mock_app.config = {
            "MAX_CONTENT_LENGTH": 1024,
            "ALLOWED_EXTENSIONS": {"png"},
            "UPLOAD_FOLDER": str(self.upload_dir)
        }
        
        file_data = BytesIO(b"fake image content")
        file_storage = FileStorage(stream=file_data, filename="avatar.png", content_type="image/png")
        
        # Mock create_file to return successfully
        fake_record = UploadedFile(id=10, original_filename="avatar.png", stored_filename="hash.png", file_path="/static/uploads/event_posters/hash.png")
        self.mock_dao.create_file.return_value = fake_record
        self.mock_dao.get_files_by_event.return_value = []

        res = self.file_service.save_poster(file_storage, event_id=5, user_id=1)
        
        assert res["success"] is True
        assert res["status"] == 201
        assert "event_posters" in os.listdir(self.upload_dir)

    @patch("flask.current_app")
    def test_save_poster_invalid_extension(self, mock_app):
        """WHY: Unsupported file extensions like .exe must be rejected immediately."""
        mock_app.config = {
            "MAX_CONTENT_LENGTH": 1024,
            "ALLOWED_EXTENSIONS": {"png"},
            "UPLOAD_FOLDER": str(self.upload_dir)
        }
        
        file_data = BytesIO(b"dangerous code")
        file_storage = FileStorage(stream=file_data, filename="malicious.exe", content_type="application/octet-stream")
        
        res = self.file_service.save_poster(file_storage, event_id=1, user_id=1)
        assert res["success"] is False
        assert "Unsupported file extension" in res["message"]
        assert res["status"] == 400

    @patch("flask.current_app")
    def test_save_poster_invalid_mime(self, mock_app):
        """WHY: Safe extension but non-image mime type must be rejected."""
        mock_app.config = {
            "MAX_CONTENT_LENGTH": 1024,
            "ALLOWED_EXTENSIONS": {"png"},
            "UPLOAD_FOLDER": str(self.upload_dir)
        }
        
        file_data = BytesIO(b"some text data")
        file_storage = FileStorage(stream=file_data, filename="doc.png", content_type="text/plain")
        
        res = self.file_service.save_poster(file_storage, event_id=1, user_id=1)
        assert res["success"] is False
        assert "must be an image type" in res["message"]

    @patch("flask.current_app")
    def test_save_poster_too_large(self, mock_app):
        """WHY: Files exceeding maximum size limits must fail validation."""
        mock_app.config = {
            "MAX_CONTENT_LENGTH": 5, # 5 bytes limit
            "ALLOWED_EXTENSIONS": {"png"},
            "UPLOAD_FOLDER": str(self.upload_dir)
        }
        
        file_data = BytesIO(b"too large image content")
        file_storage = FileStorage(stream=file_data, filename="big.png", content_type="image/png")
        
        res = self.file_service.save_poster(file_storage, event_id=1, user_id=1)
        assert res["success"] is False
        assert "exceeds limit" in res["message"]
