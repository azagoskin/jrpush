from __future__ import annotations
import dataclasses
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Sequence, Tuple

__all__ = ("Config", "TimeTrackingItemDC")


DATEFORMAT = "%Y%m%dT%H%M%SZ"
TAG_HEADER = "tags"
ANNOTATION_HEADER = "annotation"
START_HEADER = "start"
END_HEADER = "end"


@dataclass(init=False)
class Config:
    url: str
    token: str
    username: str
    issue_pattern: str
    valid_types: Tuple[str]

    def __init__(self, raw_configuration: str):
        fields = {field.name for field in dataclasses.fields(self)}

        for line in raw_configuration.split('\n'):
            key, value = line.split(": ")
            cleaned_key = key.replace('jira.', '')
            if cleaned_key in fields:
                setattr(self, cleaned_key, value)


@dataclass
class TimeTrackingItemDC:
    username: str
    issue_id: Optional[str]
    issue_name: str
    started_date: str
    seconds: int
    annotation: Optional[str]
    type: Optional[int]

    def as_body(self) -> dict:
        body = {
            "started": self.started_date,
            "worker": self.username,
            "timeSpentSeconds": self.seconds,
            "originTaskId": self.issue_id
        }
        if self.annotation:
            body["comment"] = self.annotation
        if self.type:
            body["attributes"] = {
                "_activity_": {
                    "value": self.type
                }
            }

        return body

    @staticmethod
    def _convert_datetimes(start: str, end: str):
        start_dt = datetime.strptime(start, DATEFORMAT)
        end_dt = datetime.strptime(end, DATEFORMAT)
        interval = end_dt - start_dt
        seconds = (interval.seconds // 60 if interval.seconds > 60 else 1) * 60
        started_date = end_dt.strftime("%Y-%m-%d")
        return seconds, started_date

    @staticmethod
    def _get_issue_name(tags: Sequence[str], pattern: str) -> Optional[str]:
        issue_names = [tag for tag in tags if re.search(pattern, tag)]
        if len(issue_names) > 1:
            raise Exception(f"More than one tag: {issue_names}")

        return issue_names[0] if issue_names else None

    @staticmethod
    def _get_issue_type(
        tags: Sequence[str], valid_types: Tuple[str]
    ) -> Optional[str]:
        types = [tag for tag in tags if tag in valid_types]
        if len(types) > 1:
            raise Exception(f"More than one type: {types}")

        return types[0] if types else None

    @classmethod
    def load_many(cls, tw_body: str, config: Config) -> List[TimeTrackingItemDC]:
        timetracks: List[TimeTrackingItemDC] = []

        for raw_timetrack in json.loads(tw_body):
            tags = raw_timetrack.get(TAG_HEADER, ())
            issue_name = cls._get_issue_name(tags, config.issue_pattern)
            timetrack_type = cls._get_issue_type(tags, config.valid_types)
            seconds, started_date = cls._convert_datetimes(
                raw_timetrack.get(START_HEADER),
                raw_timetrack.get(END_HEADER)
            )

            if issue_name:
                timetracks.append(
                    cls(
                        username=config.username,
                        issue_id=None,
                        issue_name=issue_name,
                        annotation=raw_timetrack.get(ANNOTATION_HEADER),
                        seconds=seconds,
                        started_date=started_date,
                        type=timetrack_type
                    )
                )

        return timetracks
