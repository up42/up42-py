import json
from typing import Dict


def match_request_body(data: dict):
    def matcher(request):
        return request.text == json.dumps(data)

    return matcher
