from google.cloud import secretmanager
from google.auth import default

_, GCP_PROJECT = default()


class GCPSecrets:
    def __init__(self) -> None:
        self.client = secretmanager.SecretManagerServiceClient()
        self.base_url = f"projects/{GCP_PROJECT}/secrets"

    def get_secret(self, secret: str):
        secret_response = self.client.access_secret_version(
            name=f"{self.base_url}/{secret}/versions/latest"
        )
        creds = secret_response.payload.data.decode("UTF-8")
        return creds
