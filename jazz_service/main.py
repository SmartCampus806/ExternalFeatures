import base64
import datetime
import json
import os
import uuid

import jwt
import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import HTTPException, FastAPI

app = FastAPI()

# Constants
SBERJAZZ_SDK_CLOUD_KEY_ENV_VAR = 'SBERJAZZ_SDK_CLOUD_KEY'
ALLOWED_IPS = ["192.168.1.1", "10.0.0.1", '127.0.0.1']
JAZZ_API_BASE_URL = "https://api.jazz.sber.ru/v1"

# Global variables
cloud_key_data = None


async def load_and_decode_cloud_key():
    global cloud_key_data
    encoded_cloud_key = os.environ.get(SBERJAZZ_SDK_CLOUD_KEY_ENV_VAR)
    if not encoded_cloud_key:
        raise ValueError(f"Environment variable '{SBERJAZZ_SDK_CLOUD_KEY_ENV_VAR}' is not set")

    decoded_bytes = base64.b64decode(encoded_cloud_key)
    decoded_str = decoded_bytes.decode('utf-8')
    cloud_key_data = json.loads(decoded_str)


@app.on_event("startup")
async def startup_event():
    await load_and_decode_cloud_key()


def get_private_key_from_cloud_key_data() -> str:
    key_data = cloud_key_data["key"]
    d_bytes = base64.urlsafe_b64decode(key_data['d'] + '===')
    private_key = ec.derive_private_key(
        int.from_bytes(d_bytes, byteorder='big'),
        ec.SECP384R1(),
        default_backend()
    )
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return private_pem.decode('utf-8')


def update_cloud_key_in_env(encoded_cloud_key: str):
    try:
        os.environ[SBERJAZZ_SDK_CLOUD_KEY_ENV_VAR] = encoded_cloud_key
        load_and_decode_cloud_key()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def call_jazz_api(url: str, method: str = "GET", payload: dict = None, headers: dict = None) -> dict:
    if headers is None:
        headers = {}
    if payload is None:
        payload = {}
    response = requests.request(method, url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()


def generate_transport_token() -> str:
    issued_at = datetime.datetime.utcnow()
    expires_at = issued_at + datetime.timedelta(hours=1)
    jwt_id = str(uuid.uuid4())
    subject = str(uuid.uuid4())

    payload = {
        "iat": issued_at,
        "exp": expires_at,
        "jti": jwt_id,
        "sdkProjectId": cloud_key_data.get("projectId"),
        "sub": subject
    }

    headers = {'kid': cloud_key_data["key"].get("kid"), 'alg': 'ES384', 'typ': 'JWT'}
    private_key_str = get_private_key_from_cloud_key_data()
    encoded_jwt = jwt.encode(payload=payload, key=private_key_str, algorithm='HS256', headers=headers)
    return encoded_jwt


def jazz_login() -> str:
    url = f"{JAZZ_API_BASE_URL}/auth/login"
    headers = {'Accept': 'application/json', 'Authorization': f'Bearer {generate_transport_token()}'}
    response_json = call_jazz_api(url, method="POST", headers=headers)
    return response_json.get('token')


def get_jazz_room_info(access_token: str, room_title: str) -> dict:
    url = f"{JAZZ_API_BASE_URL}/room/create"
    payload = {"roomTitle": room_title}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'Bearer {access_token}'}
    return call_jazz_api(url, method="POST", payload=payload, headers=headers)


@app.get("/conference-link")
async def generate_jazz_conference_link_api(room_title: str) -> dict:
    """
    Generate a conference link for a Jazz room with the given title.

    Args:
        room_title (str): The title of the Jazz room.

    Returns:
        json: Containing the response from Jazz API with the conference link details.
    """
    access_token = jazz_login()
    return get_jazz_room_info(access_token, room_title)