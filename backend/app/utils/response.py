from flask import jsonify

def api_response(data=None, message="Success", status_code=200, success=True):
    """
    Standardized API response wrapper matching:
    { "success": true/false, "data": {}, "message": "..." }
    """
    if data is None:
        data = {}
    return jsonify({
        "success": success,
        "data": data,
        "message": message
    }), status_code


def error_response(message="An error occurred", status_code=400, data=None):
    """
    Standardized Error response wrapper.
    """
    if data is None:
        data = {}
    return jsonify({
        "success": False,
        "data": data,
        "message": message
    }), status_code
