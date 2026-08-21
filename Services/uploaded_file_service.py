# Services/uploaded_file_service.py
#
# Business logic for uploaded files (metadata only — the file itself lives
# on disk under static/uploads/).
#
# SCOPE for THIS phase:
#   - create a metadata row (the caller supplies everything)
#   - read one / list by user / list by event
#   - delete a metadata row (deleting the physical file is the caller's job)
#
# What this service does NOT do in this phase:
#   - accept a multipart file upload from the request
#   - save the physical bytes to disk
#   - validate file types
#   - generate thumbnails / unique stored filenames
#
# Those belong to a later file-handling workflow and will wrap these methods.

from DAO import UploadedFileDAO
from models.uploaded_file import UploadedFile
from api.serializers import _ser
from Services._result import ok, fail


def file_to_dict(f):
    return {
        "id": f.id,
        "user_id": f.user_id,
        "event_id": f.event_id,
        "original_filename": f.original_filename,
        "stored_filename": f.stored_filename,
        "file_path": f.file_path,
        "file_type": f.file_type,
        "file_size": f.file_size,
        "uploaded_at": _ser(f.uploaded_at),
    }


class UploadedFileService:
    def __init__(self):
        self.file_dao = UploadedFileDAO()

    def create_file(self, data: dict) -> dict:
        required = ("original_filename", "stored_filename", "file_path")
        for f in required:
            v = data.get(f)
            if v is None or (isinstance(v, str) and not v.strip()):
                return fail(f"Missing required field: {f}", 400)

        u = UploadedFile(
            user_id=data.get("user_id"),
            event_id=data.get("event_id"),
            original_filename=data["original_filename"],
            stored_filename=data["stored_filename"],
            file_path=data["file_path"],
            file_type=data.get("file_type"),
            file_size=data.get("file_size"),
        )
        try:
            saved = self.file_dao.create_file(u)
        except Exception:
            return fail("Could not create uploaded file record", 500)
        return ok("Uploaded file record created",
                  file_to_dict(saved), status=201)

    def get_file_by_id(self, file_id: int) -> dict:
        f = self.file_dao.get_file_by_id(file_id)
        if f is None:
            return fail("Uploaded file not found", 404)
        return ok("Uploaded file retrieved", file_to_dict(f))

    def get_files_by_user(self, user_id: int) -> dict:
        rows = self.file_dao.get_files_by_user(user_id)
        return ok("User files retrieved", [file_to_dict(f) for f in rows])

    def get_files_by_event(self, event_id: int) -> dict:
        rows = self.file_dao.get_files_by_event(event_id)
        return ok("Event files retrieved", [file_to_dict(f) for f in rows])

    def delete_file(self, file_id: int) -> dict:
        f = self.file_dao.get_file_by_id(file_id)
        if f is None:
            return fail("Uploaded file not found", 404)
        try:
            self.file_dao.delete_file(f)
        except Exception:
            return fail("Could not delete uploaded file record", 500)
        return ok("Uploaded file record deleted")
