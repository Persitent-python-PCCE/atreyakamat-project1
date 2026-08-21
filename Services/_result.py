# Services/_result.py
#
# Tiny helper used by every Service so that the return shape is consistent.
#
# A Service method ALWAYS returns a plain dict with this shape:
#
#     {
#         "success": True/False,         # required
#         "message": "short text",        # required
#         "data": anything,               # optional (omitted on errors)
#         "status": 200,                  # optional HTTP code hint
#     }
#
# A Service NEVER imports Flask, never calls jsonify(), never reads the
# HTTP request. It only takes plain Python arguments and returns a dict.
# The Controller (api/*_routes.py) turns this dict into an HTTP response.
#
# Keeping the helper here means every Service file stays short and the
# response shape can never drift between services.

def ok(message="OK", data=None, status=200):
    """Build a success result dict."""
    result = {"success": True, "message": message, "status": status}
    if data is not None:
        result["data"] = data
    return result


def fail(message="Failed", status=400):
    """Build an error result dict. Errors never carry `data`."""
    return {"success": False, "message": message, "status": status}
