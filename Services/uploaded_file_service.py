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

    def save_poster(self, file_storage, event_id, user_id) -> dict:
        """
        WHY: Saves an uploaded event poster file locally to disk under static/uploads/event_posters/,
        validates file extension, type and size, cleans up any old poster, and stores metadata.
        """
        import os
        import uuid
        from werkzeug.utils import secure_filename
        from flask import current_app

        # 1. Resolve configuration values
        max_size = current_app.config.get("MAX_CONTENT_LENGTH", 5 * 1024 * 1024) if current_app else 5 * 1024 * 1024
        allowed_ext = current_app.config.get("ALLOWED_EXTENSIONS", {"jpg", "jpeg", "png", "webp"}) if current_app else {"jpg", "jpeg", "png", "webp"}
        upload_folder = current_app.config.get("UPLOAD_FOLDER") if current_app else os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")

        # 2. Validate File Presence
        if not file_storage or not file_storage.filename:
            return fail("No file selected", 400)

        # 3. Validate Extension
        filename = file_storage.filename
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in allowed_ext:
            return fail(f"Unsupported file extension: .{ext}. Allowed: {', '.join(allowed_ext)}", 400)

        # 4. Validate MIME Type
        mime_type = getattr(file_storage, "content_type", "")
        if mime_type and not mime_type.startswith("image/"):
            return fail("File must be an image type", 400)

        # 5. Validate File Size
        file_storage.seek(0, os.SEEK_END)
        size = file_storage.tell()
        file_storage.seek(0)
        if size > max_size:
            return fail(f"File size exceeds limit of {max_size / (1024 * 1024)} MB", 400)

        # 6. Generate secure, unique filename to prevent path traversal and duplicates
        sec_name = secure_filename(filename)
        if not sec_name:
            sec_name = f"poster_{event_id or 'default'}_{uuid.uuid4().hex[:8]}.{ext}"
        stored_name = f"{uuid.uuid4().hex}_{sec_name}"

        # 7. Write to Local Filesystem
        posters_dir = os.path.join(upload_folder, "event_posters")
        os.makedirs(posters_dir, exist_ok=True)
        full_path = os.path.join(posters_dir, stored_name)

        try:
            file_storage.save(full_path)
        except Exception as e:
            return fail(f"Could not save file to disk: {str(e)}", 500)

        # Relative path for web serving
        web_path = f"/static/uploads/event_posters/{stored_name}"

        # 8. Clean up existing posters for this event to avoid orphaned files
        if event_id:
            old_files = self.file_dao.get_files_by_event(event_id)
            for old_f in old_files:
                old_path = os.path.join(upload_folder, "event_posters", old_f.stored_filename)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception:
                        pass
                try:
                    self.file_dao.delete_file(old_f)
                except Exception:
                    pass

        data = {
            "user_id": user_id,
            "event_id": event_id,
            "original_filename": filename,
            "stored_filename": stored_name,
            "file_path": web_path,
            "file_type": mime_type or f"image/{ext}",
            "file_size": size
        }

        return self.create_file(data)

    def delete_event_posters(self, event_id: int) -> dict:
        """
        WHY: Deletes all local posters on disk and in database metadata for a deleted event.
        """
        import os
        from flask import current_app
        upload_folder = current_app.config.get("UPLOAD_FOLDER") if current_app else os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
        old_files = self.file_dao.get_files_by_event(event_id)
        for old_f in old_files:
            old_path = os.path.join(upload_folder, "event_posters", old_f.stored_filename)
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass
            try:
                self.file_dao.delete_file(old_f)
            except Exception:
                pass
        return ok("Event posters deleted successfully")
