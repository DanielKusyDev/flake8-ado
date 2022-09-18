from typing import List

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication


class AzureDevOpsClient:
    def __init__(self, access_token: str, organization_url: str) -> None:
        credentials = BasicAuthentication("", access_token)
        connection = Connection(base_url=organization_url, creds=credentials)
        self._client = connection.clients.get_work_item_tracking_client()

    def get_not_existing_item_ids(self, ids: List[str]) -> List[str]:
        work_items = self._client.get_work_items(ids=ids, error_policy="Omit")
        not_existing_ids = set(ids) - {item.id for item in work_items if item}
        return list(not_existing_ids)
