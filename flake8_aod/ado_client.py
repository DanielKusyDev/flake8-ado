from typing import List

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

from tests.settings import ADO_ACCESS_TOKEN, ADO_ORGANIZATION_URL


class AzureDevOpsClient:
    def __init__(self) -> None:
        credentials = BasicAuthentication("", ADO_ACCESS_TOKEN)
        connection = Connection(base_url=ADO_ORGANIZATION_URL, creds=credentials)
        self._client = connection.clients.get_work_item_tracking_client()

    def get_not_exiting_item_ids(self, ids: List[str]) -> List[str]:
        work_items = self._client.get_work_items(ids=ids, error_policy="Omit")
        not_existing_ids = set(ids) - {item.id for item in work_items if item}
        return list(not_existing_ids)
