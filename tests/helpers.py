import json


def match_request_body(data: dict):
    def matcher(request):
        return request.text == json.dumps(data)

    return matcher
