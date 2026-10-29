import csv
import logging
import re
from redminelib import Redmine
from redminelib.exceptions import BaseRedmineError
from redmine_client import redmine_client
from dotenv import load_dotenv
load_dotenv()
import os
import sys

def create_redmine_client():
    try:
        api_key = os.getenv("REDMINE_API_KEY")
        if not api_key:
            raise ValueError("REDMINE_API_KEY is not configured")
        redmine = Redmine("http://localhost:3000/", key=api_key)
        return redmine_client(redmine)
    except BaseRedmineError as e:
        raise e
    except ValueError as e:
        raise e

def configure_logging():
    logging.basicConfig(filename='eng_change_tracker.log', level=logging.INFO)
    return logging.getLogger(__name__)

def read_csv_data(path: str) -> list[list[str]]:
    try:
        with open(path, "r", encoding="utf-8", newline="") as file:
            parsed_csv =  list(csv.reader(file, delimiter=";"))
            if not parsed_csv:
                raise ValueError(f"Invalid csv file {path}")
            header = parsed_csv[0]
            print(header)
            if  len(header) != 6 or "id" not in header[0] or header[1] != "title" or header[2] != "description" or header[3] != "priority" or header[4] != "status" or header[5] != "contact":
                raise ValueError(f"Invalid csv file {path}")
            return parsed_csv
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found {path}")
    except UnicodeDecodeError:
        raise UnicodeDecodeError(f"File not found {path}")

class work_request:
    def __init__(self, id, title, description, priority, status, contact):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.contact = contact
        self.log = ""

    def validate(self, id_list: set[str]) -> bool:
        if not self.id:
            self.log += "Empty Id; "
        if self.id in id_list:
            self.log += f"{self.id} Id is already taken; "
        if not self.title:
            self.log += "Empty title; "
        if self.priority not in ["High", "Medium", "Low"]:
            self.log += f"Invalid priority: {self.priority}; "
        if not self.status:
            self.log += "Empty status; "
        if self.status not in ["open", "closed", "new"]:
            self.log += f"Invalid status: {self.status}; "
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.contact):
            self.log += f"Invalid contact: {self.contact}; "
        if self.description is None:
            self.log += "Empty description; "
        if self.log:
            return False
        return True

    def __str__(self):
        if self.log:
            return f"Request could not be created. REASON: {self.log}"
        return f"{self.id} {self.title} {self.description} {self.priority} {self.status} {self.contact}"

class run_report:
    def __init__(self, valid_reqs, invalid_reqs):
        self.valid_reqs = valid_reqs
        self.invalid_reqs = invalid_reqs
        self.log = ""

    def report_log(self) -> str:
        lines = [f"{len(self.valid_reqs)} Valid Requests:"]
        for req in self.valid_reqs:
            lines.append(
                f"{req.id}: {req.title}; {req.description}; "
                f"{req.priority}; {req.status}; {req.contact}"
            )
        if self.invalid_reqs:
            lines.append(f"{len(self.invalid_reqs)} Invalid Requests:")
            for req in self.invalid_reqs:
                lines.append(str(req))

        return "\n".join(lines) + "\n"

    def save_log(self):
        with open("run_report.log", "a") as f:
            f.write(self.report_log())
            f.write("===============\n")

def create_work_request(row: list[str]):
    #Check for type validation non csv data
    if len(row) != 6:
        raise ValueError(f"Invalid record: {row}. Invalid number of arguments {len(row)}")
    id, title, description, priority, status, contact = row
    if [x for x in [id, title, description, priority, status, contact] if not isinstance(x, str)]:
        raise TypeError("Invalid data type provided")
    return work_request(id, title, description, priority, status, contact)

if __name__ == '__main__':
    #init the variables
    if len(sys.argv) != 3:
        sys.exit("Invalid number of arguments")
    logger = configure_logging()
    path = sys.argv[1]
    project = sys.argv[2]
    try:
        parsec_csv = read_csv_data(path)
        redmine_client = create_redmine_client()
    except Exception as e:
        logging.error(e)
        sys.exit(e)
    #Temp variables
    valid_wk_rqs = []
    valid_wk_rqs_ids = set()
    invalid_wk_rqs = []
    #Read work request, separate by validity
    for index, row in enumerate(parsec_csv):
        try:
            work_req = create_work_request(row)
            if work_req.validate(valid_wk_rqs_ids):
                valid_wk_rqs.append(work_req)
                valid_wk_rqs_ids.add(work_req.id)
            else:
                invalid_wk_rqs.append(work_req)
        except TypeError:
            invalid_wk_rqs.append(f"Invalid data type provided {index}: {row}. Request could not be created.")
        except ValueError as e:
            invalid_wk_rqs.append(e)
    #output log from read
    operation_report = run_report(valid_wk_rqs, invalid_wk_rqs)
    operation_report.save_log()
    #save valid requests to Redmine
    #TODO: log Redmine API export
    for work_req in valid_wk_rqs:
        redmine_client.create_issue(work_req.title, work_req.description, work_req.priority, work_req.status, project)
