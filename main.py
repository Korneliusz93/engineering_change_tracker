import csv
import json
import pathlib
import logging
import re

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

    def validate_id(self, id_list) -> bool:
        if not self.id:
            self.log += "Id is empty\n"
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
        if not self.priority:
            self.log += "Empty priority; "
            return False
        if self.priority not in ["high", "medium", "low"]:
            self.log += f"Invalid priority: {self.priority}; "
            return False
        return True

    def validate_status(self) -> bool:
        if not self.status:
            self.log += "Empty status; "
            return False
        return True

    def validate_contact(self) -> bool:
        if re.match(r"[^@]+@[^@]+\.[^@]+", self.contact):
            return True
        return False

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
                else:
                    self.log += f"{req}\n"

    def __str__(self):
        return self.log

def create_work_request(id, title, description, priority, status, contact):
    return work_request(id, title, description, priority, status, contact)

def validate_work_request(work_request: work_request, work_reqs_ids) -> bool:
    try:
        if not work_request:
            return False
        is_id_valid = work_request.validate_id(work_reqs_ids)
        is_prio_valid = work_request.validate_priority()
        is_title_valid = work_request.validate_title()
        is_status_valid = work_request.validate_status()
        is_contact_valid = work_request.validate_contact()
        if is_id_valid and is_prio_valid and is_title_valid and is_status_valid and is_contact_valid:
            return True
        else:
            return False
    #TODO: write more exceptions
    except AttributeError:
        work_request.log += "Invalid attribute"
        return False

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(filename='eng_change_tracker.log', level=logging.INFO)
    path = "/Users/admin/PycharmProjects/    engineering_change_tracker/sample_data/sample_data1.csv"
    parsec_csv = read_csv_data(path)
    valid_wk_rqs = []
    valid_wk_rqs_ids = set()
    invalid_wk_rqs = []
    for index, row in enumerate(parsec_csv):
        if len(row) != 6:
            invalid_wk_rqs.append(f"Invalid record at line {index}: {row}. Request could not be created.")
            continue
        work_req = create_work_request(row[0], row[1], row[2], row[3], row[4], row[5])
        if validate_work_request(work_req, valid_wk_rqs_ids):
            valid_wk_rqs.append(work_req)
            valid_wk_rqs_ids.add(work_req.id)
        else:
            invalid_wk_rqs.append(work_req)
    operation_report = run_report(valid_wk_rqs, invalid_wk_rqs)
    operation_report.report_log()
    print(operation_report)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
