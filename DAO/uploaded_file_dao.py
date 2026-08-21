# DAO/uploaded_file_dao.py
#
# UploadedFileDAO — Data Access Object for the `uploaded_files` table.
# Each row stores *metadata* about an uploaded file (event images, venue
# images, user ID documents). The actual file lives on disk under
# static/uploads/. The DAO never reads or writes the file on disk — only
# its database row.

from app import db
from models.uploaded_file import UploadedFile


class UploadedFileDAO:
    """Database operations for the UploadedFile model."""

    def create_file(self, uploaded_file: UploadedFile) -> UploadedFile:
        """Insert a new uploaded-file metadata row.

        The Service is expected to set: user_id (or None), event_id (or None),
        original_filename, stored_filename, file_path, file_type, file_size.
        The DAO just persists it.
        """
        try:
            db.session.add(uploaded_file)
            db.session.commit()
            return uploaded_file
        except Exception:
            db.session.rollback()
            raise

    def get_file_by_id(self, file_id: int) -> UploadedFile | None:
        """Load one uploaded-file metadata row by its primary key."""
        return db.session.get(UploadedFile, file_id)

    def get_files_by_user(self, user_id: int) -> list[UploadedFile]:
        """Return every file uploaded by a given user."""
        return UploadedFile.query.filter_by(user_id=user_id).all()

    def get_files_by_event(self, event_id: int) -> list[UploadedFile]:
        """Return every file attached to a given event (e.g. event posters)."""
        return UploadedFile.query.filter_by(event_id=event_id).all()

    def update_file(self, uploaded_file: UploadedFile) -> UploadedFile:
        """Commit changes the Service already applied to `uploaded_file`."""
        try:
            db.session.commit()
            return uploaded_file
        except Exception:
            db.session.rollback()
            raise

    def delete_file(self, uploaded_file: UploadedFile) -> bool:
        """Delete the metadata row only. Returns True on success.

        NOTE: deleting the physical file on disk is the Service's job,
        not the DAO's. The DAO only removes the database row.
        """
        try:
            db.session.delete(uploaded_file)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            raise
