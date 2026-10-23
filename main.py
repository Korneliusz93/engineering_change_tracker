import csv
import logging
import re
from redminelib import Redmine
from redmine_client import redmine_client
from dotenv import load_dotenv
load_dotenv()
import os
import sys

def create_redmine_client():
    api_key = os.getenv("REDMINE_API_KEY")
    redmine = Redmine("http://localhost:3000/", key=api_key)
    return redmine_client(redmine)

def configure_logging():
    logging.basicConfig(filename='eng_change_tracker.log', level=logging.INFO)
    return logging.getLogger(__name__)

def read_csv_data(path: str) -> list[list[str]]:
    with open(path, "r", encoding="utf-8", newline="") as file:
        return list(csv.reader(file, delimiter=";"))

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
            self.log += f"Invalid status: {self.priority}; "
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

def create_work_request(id, title, description, priority, status, contact):
    #Check for type validation non csv data
    if [x for x in [id, title, description, priority, status, contact] if not isinstance(x, str)]:
        raise TypeError("Invalid data type provided")
    return work_request(id, title, description, priority, status, contact)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #init the variables
    if len(sys.argv) != 3:
        sys.exit("Invalid number of arguments")
    path = sys.argv[1]
    project = sys.argv[2]
    parsec_csv = read_csv_data(path)

    redmine_client = create_redmine_client()
    logger = configure_logging()
    #temp variables
    valid_wk_rqs = []
    valid_wk_rqs_ids = set()
    invalid_wk_rqs = []
    #Read work request, separate by validity
    for index, row in enumerate(parsec_csv):
        try:
            if len(row) != 6:
                invalid_wk_rqs.append(f"Invalid record at line {index}: {row}. Request could not be created.")
                continue
            work_req = create_work_request(row[0], row[1], row[2], row[3], row[4], row[5])
            print(work_req)
            if work_req.validate(valid_wk_rqs_ids):
                valid_wk_rqs.append(work_req)
                valid_wk_rqs_ids.add(work_req.id)
            else:
                invalid_wk_rqs.append(work_req)
        except TypeError:
            invalid_wk_rqs.append(f"Invalid data type provided {index}: {row}. Request could not be created.")
    #output log from read
    operation_report = run_report(valid_wk_rqs, invalid_wk_rqs)
    operation_report.report_log()
    operation_report.save_log()
    #save valid requests to Redmine
    #TODO: log Redmine API export
    for work_req in valid_wk_rqs:
        print(work_req.title)
        redmine_client.create_issue(work_req.title, work_req.description, work_req.priority,
                        work_req.status,project)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
