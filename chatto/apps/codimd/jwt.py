from rest_framework_jwt.utils import jwt_encode_handler, jwt_decode_handler
from datetime import datetime, timedelta


def jwt_gid(gid):
    payload = {  # 新建用户专用
        'gid': str(gid),  # game id
        'exp': datetime.utcnow() + timedelta(seconds=60)
    }
    return jwt_encode_handler(payload)


def jwt_user(gid, user):
    payload = {  # 新建用户专用
        'gid': gid,  # game id
        'uid': user.id,  # user id
        'exp': datetime.utcnow() + timedelta(seconds=60)
    }
    return jwt_encode_handler(payload)


def jwt_token(gid, user):
    payload = {  # 新建用户专用
        'id': "%s/%s" % (gid % user.id),  # game id
        'exp': datetime.utcnow() + timedelta(seconds=3600)
    }
    return jwt_encode_handler(payload)

