#!/usr/bin/python3
import sys

from tw_jira.logger import Logger
from tw_jira.schemas import Config, TimeTrackingItemDC
from tw_jira.jira_accessor import JiraAccessor


if __name__ == "__main__":
    summary_time = 0
    raw_configuration, raw_timetracks = sys.stdin.read().split('\n\n')

    config = Config(raw_configuration)
    logger = Logger()
    jr_accessor = JiraAccessor(config, logger)

    jr_accessor.check_connection()
    jr_accessor.set_work_item_types()

    timetracks = TimeTrackingItemDC.load_many(raw_timetracks, config)

    for timetrack in timetracks:
        jr_accessor.check_issue(timetrack)
        jr_accessor.load_time_track(timetrack)
        summary_time += timetrack.seconds

    logger(f"Summary: {summary_time // 60} mins")
