import requests


def handler(event, context):
    try:
        url = "http://18.153.175.246:8080/api/admin/check-health"
        _ = requests.get(url)

        # no error info
        error = False
        error_message = None

    # error info
    except Exception as e:
        error = True
        error_message = str(e)

    return {
        "function_name": "Bolt-PO-CheckHealth",
        "error": error,
        "error_message": error_message
    }
