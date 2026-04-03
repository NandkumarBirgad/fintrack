from flask import jsonify


def success(data=None, message="Success", status=200, meta=None):
    """Standard success envelope."""
    body = {"success": True, "message": message}
    if data is not None:
        body["data"] = data
    if meta is not None:
        body["meta"] = meta
    return jsonify(body), status


def error(message="An error occurred", status=400, errors=None):
    """Standard error envelope."""
    body = {"success": False, "message": message}
    if errors is not None:
        body["errors"] = errors
    return jsonify(body), status
