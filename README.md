# TimeWarrior Jira Tempo Push
## Summary
**jrpush** - [TimeWarrior](https://timewarrior.net/docs/api/) extension for uploading timelog to Jira Tempo. Task URLs and types (review, documentation, development, etc.) are taken from tags.

Interval intersections are not tracked
## Installation
Copy the files to the directory ~/.timewarrior/extensions:
```
$ ls -la ~/.timewarrior/extensions/
drwx------ 6 4096 окт  1 21:12 .
drwx------ 5 4096 окт  1 14:50 ..
drwxr-xr-x 3 4096 окт  1 21:19 tw_jira
-rwxr--r-- 1 1340 окт  1 21:12 jrpush.py
```
```
$ sudo chmod 744 ytpush.py
```
## Configuration
Add parameters to the `~/.timewarrior/timewarrior.cfg`:
```
jira.token=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
jira.url=jira.mysite.ru
jira.issue_pattern=^ABCD-\d{3,4}$
```
where `^ABCD-\d{3,4}$` is a regular expression for searching for the task name in tags
## Usage
Usage command example:
```
$ timew summary

Wk  Date       Day Tags                     Start      End    Time   Total
W39 2023-10-01 Sun Documentation, ABCD-4681 10:00:00 10:10:00 0:10:00 0:10:00

                                                                      0:10:00
$ timew jrpush 2023-10-01
[OK] Connection to jira.mysite.ru
[OK] Load work item types
[OK] Check issue ABCD-4681
[OK] Track 10 mins to ABCD-4681
Summary: 10mins
```
## PS
If something doesn't work, check the endpoints in JiraAccessor/ENDPOINTS, in your case they may be different.
