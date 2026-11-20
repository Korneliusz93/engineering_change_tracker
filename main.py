import csv
import logging
import re
from dataclasses import dataclass
from redminelib import Redmine
from redminelib.exceptions import BaseRedmineError, AuthError, ResourceNotFoundError, ServerError
from redmine_client import redmine_client
from dotenv import load_dotenv
load_dotenv()
import os
import sys


@dataclass
class CustomField:
    id: int
    value: str

def create_redmine_client(redmine_server: str, project_id: str):
    api_key = os.getenv("REDMINE_API_KEY")
    if not api_key:
        raise ValueError("REDMINE_API_KEY is not configured")
    if not redmine_server.strip() or not project_id.strip():
        raise ValueError("Redmine server and project ID are required")
    redmine = Redmine(redmine_server, key=api_key)
    return redmine_client(redmine, project_id)

def configure_logging():
    logging.basicConfig(filename='eng_change_tracker.log', level=logging.INFO)
    return logging.getLogger(__name__)

def read_csv_data(path: str) -> list[list[str]]:
    with open(path, "r", encoding="utf-8", newline="") as file:
        parsed_csv =  list(csv.reader(file, delimiter=";"))
        if not parsed_csv:
            raise ValueError(f"Invalid csv file {path}")
        header = parsed_csv[0]
        if  len(header) != 6 or "id" not in header[0] or header[1] != "title" or header[2] != "description" or header[3] != "priority" or header[4] != "status" or header[5] != "contact":
            raise ValueError(f"Invalid csv file {path}")
        return parsed_csv
@dataclass
class Tracker:
    id: int
    name: str

class WorkRequest:
    def __init__(self, id, title, description, priority, status, contact: CustomField):
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.log = ""
        #CONFIGURATION: All fields below should be considered Custom
        self.custom_fields = {
            "contact": contact,
            "custom_id": id
        }

    def validate(self, id_list: set[str]) -> bool:
        contact = self.custom_fields["contact"].value
        checked_id = self.custom_fields["custom_id"].value
        if not checked_id:
            self.log += "Empty Id; "
        if checked_id in id_list:
            self.log += f"{checked_id} Id is already taken; "
        if not self.title:
            self.log += "Empty title; "
        if self.priority not in ["High", "Medium", "Low"]:
            self.log += f"Invalid priority: {self.priority}; "
        if not self.status:
            self.log += "Empty status; "
        if self.status not in ["open", "closed", "new"]:
            self.log += f"Invalid status: {self.status}; "
        if not re.match(r"(^(?!\.)[^@]+)(?<!\.)@([^@_]+)\.([^@\d]+?$)", contact) or re.match(r"(.*)[.]{2,}(.*)", contact):
            self.log += f"Invalid contact: {contact}; "
        if self.description is None:
            self.log += "Empty description; "
        if self.log:
            return False
        return True

    def __str__(self):
        custom_field_id = self.custom_fields["custom_id"].value
        contact = self.custom_fields["contact"].value
        if self.log:
            return f"{self.log}"
        return f"{custom_field_id} {self.title} {self.description} {self.priority} {self.status} {contact}"

class ReportMsg():
    def __init__(self, row, message):
        self.row = row
        self.message = message

class RunReport:
    def __init__(self, valid_reqsuests: list[WorkRequest], invalid_requests: list[ReportMsg]):
        self.valid_reqsuests = valid_reqsuests
        self.invalid_requests = invalid_requests
        self.dry_run = []
        self.skipped_existing_requests = []
        self.log = ""
        self.imported_count = 0

    def report_log(self) -> str:
        lines = [f"{len(self.valid_reqsuests)} Valid Requests:"]
        for request in self.valid_reqsuests:
            custom_field_id = request.custom_fields["custom_id"].value
            contact = request.custom_fields["contact"].value
            lines.append(
                f"{custom_field_id}: {request.title}; {request.description}; "
                f"{request.priority}; {request.status}; {contact}"
            )
        if self.invalid_requests:
            lines.append(f"{len(self.invalid_requests)} Invalid Requests:")
            for request in self.invalid_requests:
                lines.append("[ROW " + str(request.row) + "]: " + request.message)

        return "\n".join(lines) + "\n"

    def dry_run_report(self):
        if self.dry_run:
            with open("run_report.log", "a") as f:
                f.write("\n".join(self.dry_run))
                f.write("\n===============\n")

    def skipped_existing_requests_report(self):
        if self.skipped_existing_requests:
            with open("run_report.log", "a") as f:
                f.write("\n".join(self.skipped_existing_requests))
                f.write("\n===============\n")

    def final_report(self):
        with open("run_report.log", "a") as f:
            f.write(f"\n{self.imported_count} entries imported out of {len(self.valid_reqsuests)} read.\n")
            f.write("\n===============\n")

    def save_log(self):
        with open("run_report.log", "a") as f:
            f.write(self.report_log())
            f.write("===============\n")
        if self.dry_run:
            self.dry_run_report()

def create_work_request(row: list[str]):
    #Check for type validation non csv data
    if len(row) != 6:
        raise ValueError(f"Invalid number of arguments {len(row)}")
    #CONFIGURATION: Add all necessary Custom fields declarations and fill the value
    contact = CustomField(2,"")
    custom_id = CustomField(3, "")
    custom_id.value , title, description, priority, status, contact.value = row
    if [x for x in [custom_id.value, title, description, priority, status, contact.value] if not isinstance(x, str)]:
        raise TypeError("Invalid data type provided")
    return WorkRequest(custom_id, title, description, priority, status, contact)

if __name__ == '__main__':
    #init the variables
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        sys.exit("Invalid number of arguments")
    logger = configure_logging()
    path = sys.argv[1]
    project = sys.argv[2]
    tracker = sys.argv[4]
    if sys.argv[3] == "--local":
        server= "http://localhost:3000/"
    else:
        server = sys.argv[3]
    dry_run = False
    if len(sys.argv) == 6 and sys.argv[5]:
        if sys.argv[5] != "--dry-run":
            sys.exit("Invalid dry run argument")
        dry_run = True
    try:
        parsec_csv = read_csv_data(path)
    except (FileNotFoundError, ValueError, OSError, csv.Error) as e:
        logger.exception("Couldn't open csv file")
        sys.exit(1)
    try:
        client = create_redmine_client(server, project)
        trackers = client.get_trackers()
    except (ValueError, BaseRedmineError) as e:
        logger.exception("Couldn't connect to redmine")
        sys.exit(1)
    if not tracker in [x[1] for x in trackers]:
        logger.error(f"Tracker {tracker} not found")
        sys.exit(1)
    #select tracker
    selected_tracker = next(
        ((tracker_id, name) for tracker_id, name in trackers if name == tracker),
        None,
    )
    if selected_tracker is None:
        logger.error("Tracker %r not found", tracker)
        sys.exit(1)
    tracker_id, tracker_name = selected_tracker
    selected_tracker = Tracker(tracker_id, tracker_name)
    #Temp variables
    valid_work_requests = []
    valid_work_request_ids = set()
    invalid_work_request = []
    dry_run_logs = []
    work_requests_skipped_existing = []
    #Read work request, separate by validity
    for index, row in enumerate(parsec_csv):
        if index == 0: continue
        try:
            work_request = create_work_request(row)
            if work_request.validate(valid_work_request_ids):
                custom_id = work_request.custom_fields["custom_id"].value
                valid_work_requests.append(work_request)
                valid_work_request_ids.add(custom_id)
            else:
                invalid_work_request.append(ReportMsg(index, str(work_request)))
        except TypeError as e:
            invalid_work_request.append(ReportMsg(index, str(e)))
        except ValueError as e:
            invalid_work_request.append(ReportMsg(index, str(e)))
    #Check against existing issues redmine DB if id exists
    existing_issues = client.get_issues()
    custom_ids = {
        str(field["value"])
        for issue in existing_issues
        for field in issue.custom_fields
        if field["id"] == 3 and field["value"] is not None
    }
    #save valid requests to Redmine
    operation_report = RunReport(valid_work_requests, invalid_work_request)
    for work_request in valid_work_requests:
        custom_id = work_request.custom_fields["custom_id"].value
        if custom_id in custom_ids:
            work_requests_skipped_existing.append(f"Work request with custom_id {custom_id} already exists")
            continue
        try:
            custom_fields = [
                {"id": field.id, "value": field.value}
                for field in work_request.custom_fields.values()
            ]
            if dry_run:
                dry_run_logs.append(f"[DRY-RUN] Work request {str(work_request)} created.")
            else:
                client.create_issue(work_request.title, work_request.description, work_request.priority, work_request.status, custom_fields)
                operation_report.imported_count += 1
        except AuthError as e:
            logger.exception("Couldn't authenticate and create issue")
            break
        except BaseRedmineError as e:
            logger.exception("Couldn't create issue.")
    # output log from read
    if dry_run_logs:
        operation_report.dry_run = dry_run_logs
        operation_report.dry_run_report()
    if work_requests_skipped_existing:
        operation_report.skipped_existing_requests = work_requests_skipped_existing
        operation_report.skipped_existing_requests_report()
    operation_report.final_report()
    operation_report.save_log()