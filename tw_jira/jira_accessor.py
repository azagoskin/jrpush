import json
from http.client import HTTPSConnection, HTTPResponse

from tw_youtrack.logger import Logger
from tw_jira.schemas import TimeTrackingItemDC, Config

__all__ = ("JiraAccessor",)


class JiraAccessor:
    HEADERS = {
        "Accept": "application/json",
        "Cache-control": "no-cache",
        "Content-Type": "application/json"
    }
    ENDPOINTS = {
        "check_connection": "/rest/api/2/myself",
        "get_work_item_types": "/rest/scriptrunner/latest/custom/tempoWorkType",
        "get_issue": "/rest/api/latest/issue/",
        "load_timetrack": "/rest/tempo-timesheets/4/worklogs"
    }

    def __init__(self, config: Config, logger: Logger):
        self.config = config
        self.logger = logger
        self.url = config.url.replace("https://", "")
        self.HEADERS["Authorization"] = f"Bearer {config.token}"

    def get_request(self, endpoint: str) -> HTTPResponse:
        connection = HTTPSConnection(self.url)
        connection.request("GET", endpoint, headers=self.HEADERS)
        return connection.getresponse()

    def post_request(self, endpoint: str, body: str) -> HTTPResponse:
        connection = HTTPSConnection(self.url)
        connection.request("POST", endpoint, body=body, headers=self.HEADERS)
        return connection.getresponse()

    def check_connection(self):
        response = self.get_request(self.ENDPOINTS["check_connection"])
        data = json.loads(response.read())
        self.config.username = data.get("key")
        self.logger(f"Connection to {self.url}", response.status == 200)

    def set_work_item_types(self):
        url = self.ENDPOINTS["get_work_item_types"]
        response = self.get_request(url)
        data = response.read().decode('utf-8')
        data = data.strip('null (').rstrip(')')
        data = json.loads(data)
        self.config.valid_types = {
            item["key"] for item in data.get("values", ()) if item.get('key')
        }
        self.logger(f"Load work item types", response.status == 200)

    def check_issue(self, timetrack: TimeTrackingItemDC):
        url = self.ENDPOINTS["get_issue"] + timetrack.issue_name
        response = self.get_request(url)
        data = json.loads(response.read())
        timetrack.issue_id = data["id"]
        self.logger(
            f"Check issue {timetrack.issue_name}", response.status == 200
        )

    def load_time_track(self, timetrack: TimeTrackingItemDC):
        response = self.post_request(
            self.ENDPOINTS["load_timetrack"],
            body=json.dumps(timetrack.as_body()),
        )
        self.logger(
            f"Track {timetrack.seconds // 60} mins to {timetrack.issue_name}",
            response.status == 200
        )
