import csv
import json
import pathlib
import logging
import re
import typing
from redminelib import Redmine
from redmine_client import redmine_client

from dotenv import load_dotenv
load_dotenv()
import requests
import os

api_key = os.getenv("REDMINE_API_KEY")
load_dotenv()

def read_csv_data(path):
    with open(path, 'r') as f:
        reader = csv.reader(f,delimiter=';')
        return list(reader)

logger = logging.getLogger(__name__)

class work_request:
    def __init__(self, id, title, description, priority, status, contact):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.contact = contact
        self.log = ""

    def validate_id(self, id_list: set) -> bool:
        if not self.id:
            self.log += "Empty Id; "
            return False
        if self.id in id_list:
            self.log += f"{self.id} Id is already taken; "
            return False
        return True

    def validate_title(self) -> bool:
        if not self.title:
            self.log += "Empty title; "
            return False
        return True

    def validate_priority(self) -> bool:
        if self.priority not in ["High", "Medium", "Low"]:
            self.log += f"Invalid priority: {self.priority}; "
            return False
        return True

    def validate_status(self) -> bool:
        if not self.status:
            self.log += "Empty status; "
            return False
        if self.status not in ["open", "closed", "new"]:
            self.log += f"Invalid priority: {self.priority}; "
            return False
        return True

    def validate_contact(self) -> bool:
        if re.match(r"[^@]+@[^@]+\.[^@]+", self.contact):
            return True
        self.log += f"Invalid contact: {self.contact}; "
        return False

    def validate_description(self) -> bool:
        if self.description is None:
            self.log += "Empty description; "
            return False
        return True

    def __str__(self):
        if self.log:
            return f"Request could not be created. RESON: {self.log}"
        return f"{self.id} {self.title} {self.description} {self.priority} {self.status} {self.contact}"

class run_report:
    def __init__(self, valid_reqs, invalid_reqs):
        self.valid_reqs = valid_reqs
        self.invalid_reqs = invalid_reqs
        self.log = ""

    def report_log(self):
        self.log += f"{len(self.valid_reqs)} Valid Requests:\n"
        for req in self.valid_reqs:
            self.log += f"{req.id}: {req.title}; "
            self.log += f"{req.description}; "
            self.log += f"{req.priority}; "
            self.log += f"{req.status}; "
            self.log += f"{req.contact}\n"
        if self.invalid_reqs:
            self.log += f"{len(self.invalid_reqs)} Invalid Requests:\n"
            for req in self.invalid_reqs:
                if isinstance(req, work_request):
                    self.log += f"{req.id}: {req.title}; "
                    self.log += f"{req.description}; "
                    self.log += f"{req.priority}; "
                    self.log += f"{req.status}; "
                    self.log += f"{req.contact}\n"
                    self.log += f"{req.log}\n"
                else:
                    self.log += f"{req}\n"
    def __str__(self):
        return self.log

def create_work_request(id, title, description, priority, status, contact):
    #Check for type validation non csv data
    if [x for x in [id, title, description, priority, status, contact] if not isinstance(x, str)]:
        raise TypeError("Invalid data type provided")
    return work_request(id, title, description, priority, status, contact)

def validate_work_request(work_req: work_request, work_reqs_ids) -> bool:
    try:
        if not work_request or not isinstance(work_req, work_request):
            return False
        if not isinstance(work_reqs_ids, set):
            return False
        is_id_valid = work_req.validate_id(work_reqs_ids)
        is_prio_valid = work_req.validate_priority()
        is_title_valid = work_req.validate_title()
        is_status_valid = work_req.validate_status()
        is_contact_valid = work_req.validate_contact()
        is_description_valid = work_req.validate_description()
        if is_id_valid and is_prio_valid and is_title_valid and is_status_valid and is_contact_valid and is_description_valid:
            return True
        else:
            return False
    except AttributeError:
        raise AttributeError("Invalid data provided")
    except TypeError:
        raise TypeError("Invalid data type provided")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #init the variables
    logging.basicConfig(filename='eng_change_tracker.log', level=logging.INFO)
    path = "/Users/admin/PycharmProjects/    engineering_change_tracker/sample_data/sample_data1.csv"
    redmine = Redmine("http://localhost:3000/", key=api_key)
    parsec_csv = read_csv_data(path)
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
            if validate_work_request(work_req, valid_wk_rqs_ids):
                valid_wk_rqs.append(work_req)
                valid_wk_rqs_ids.add(work_req.id)
            else:
                invalid_wk_rqs.append(work_req)
        except TypeError:
            invalid_wk_rqs.append(f"Invalid data type provided {index}: {row}. Request could not be created.")
        except AttributeError:
            invalid_wk_rqs.append(f"Invalid data provided {index}: {row}. Request could not be created.")
    #output log from read
    operation_report = run_report(valid_wk_rqs, invalid_wk_rqs)
    operation_report.report_log()
    print(operation_report)

    #

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
