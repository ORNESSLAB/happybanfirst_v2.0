import argparse
import base64
import os
import binascii
import hashlib
from datetime import datetime, timezone

class IBanFirst:
    def __init__(self, user_id: str, password: str):
        self.user_id = user_id
        self.password = password

    def generate_header(self) -> dict:
        """
        Generate iBanFirst header with WSSE + custom fields

        :return: dict a header with wsse
        """
        # Generate random nonce
        nonce = binascii.b2a_hex(os.urandom(16))  # return byte
        # Get the current UTC timestamp in ISO 8601 format
        #date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ" )
        # Convert password and timestamp to bytes
        password_byte = self.password.encode("ascii")
        date_byte = date.encode("ascii")

        # Hash the nonce, timestamp, and password
        hashed_params = hashlib.sha1(nonce + date_byte + password_byte)

        # Encode nonce and hashed password in Base64
        nonce_64_utf = base64.b64encode(nonce).decode("utf-8")
        password_64_utf = base64.b64encode(hashed_params.digest()).decode("utf-8")

        # Construct the WSSE header string
        wsse_string = 'UsernameToken Username="{}", PasswordDigest="{}", Nonce="{}", Created="{}"'.format(
            self.user_id,
            password_64_utf,
            nonce_64_utf,
            date_byte.decode("utf-8"),
        )

        header = {
            "X-WSSE": wsse_string,
            "Content-Type": "application/json; charset=utf-8",
        }
        return header


