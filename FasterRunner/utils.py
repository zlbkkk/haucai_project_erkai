"""
JWT utilities for handling version compatibility
"""
import jwt
from rest_framework_jwt.settings import api_settings


def jwt_encode_handler(payload):
    """
    Custom JWT encode handler that handles PyJWT 2.x compatibility
    PyJWT 2.x returns str instead of bytes, so we don't need to decode
    """
    key = api_settings.JWT_PRIVATE_KEY or api_settings.JWT_SECRET_KEY
    algorithm = api_settings.JWT_ALGORITHM

    token = jwt.encode(payload, key, algorithm)

    # PyJWT 2.x returns str, PyJWT 1.x returns bytes
    # We ensure we always return str for consistency
    if isinstance(token, bytes):
        return token.decode('utf-8')
    return token


def jwt_decode_handler(token):
    """
    Custom JWT decode handler that handles PyJWT 2.x compatibility
    """
    options = {
        'verify_signature': api_settings.JWT_VERIFY,
        'verify_exp': api_settings.JWT_VERIFY_EXPIRATION,
        'verify_aud': api_settings.JWT_AUDIENCE is not None,
        'require_exp': api_settings.JWT_VERIFY_EXPIRATION,
        'require_aud': api_settings.JWT_AUDIENCE is not None
    }

    # Use the secret key and algorithm from settings
    secret_key = api_settings.JWT_PRIVATE_KEY or api_settings.JWT_SECRET_KEY
    algorithm = api_settings.JWT_ALGORITHM

    try:
        # PyJWT 2.x requires algorithms parameter
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
            options=options,
            audience=api_settings.JWT_AUDIENCE,
            issuer=api_settings.JWT_ISSUER,
            leeway=api_settings.JWT_LEEWAY
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError('Signature has expired.')
    except jwt.DecodeError:
        raise jwt.DecodeError('Error decoding signature.')
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError()
