from operator import contains

import pytest
from main import work_request, run_report, create_work_request


def test_validate_same_id():
    wr = work_request('ER-123', 'test title', 'test description', 'test prio', 'test status', 'contact@contact.com')
    id_list = {'ER-123'}
    assert wr.validate(id_list) == False
    assert "Id is already taken" in wr.log


def test_validate_title():
    wr = work_request('ER-123', '', 'test description', 'test prio', 'test status', 'contact@contact.com')
    assert wr.validate(set()) == False
    assert "Empty title" in wr.log


def test_validate_invalid_contact():
    wr = work_request('ER-123', 'test title', 'test description', 'test prio', 'test status', 'contact#contact.com')

    assert wr.validate(set()) == False
    assert "Invalid contact" in wr.log


def test_validate_work_request_invalid_request():
    wr = work_request('ER-123', '', 'test description', 'super', 'test status', 'contact#contact.com')
    req_ids = {'ER-123'}
    is_valid = wr.validate(req_ids)
    assert "Id is already taken" in wr.log
    assert "Empty title" in wr.log
    assert "Invalid priority" in wr.log
    assert "Invalid contact" in wr.log
    assert is_valid == False

def test_validate_work_request_invalid_id_list():
    wr = work_request('ER-123', 'valid', 'test description', 'high', 'test status', 'contact@contact.com')
    is_valid = wr.validate( 'ER-123')
    assert is_valid == False

def test_validate_work_request_invalid_id_list_type():
    wr = work_request('ER-123', 'valid', 'test description', 'high', 'test status', 'contact@contact.com')
    is_valid = wr.validate([23])
    assert is_valid == False

def test_validate_description_empty():
    wr = work_request('ER-123', 'valid', '', 'high', 'test status', 'contact@contact.com')
    is_valid = wr.validate({'ER-423'})
    assert is_valid == False

def test_validate_description_none():
    wr = work_request('ER-123', 'valid', None, 'high', 'test status', 'contact@contact.com')
    is_valid = wr.validate( {'ER-423'})
    assert is_valid == False
    assert "Empty description" in wr.log

def test_create_work_request_invalid_type():
    with pytest.raises(TypeError) as e:
        row = [None, 'valid', 'test description', 'high', 'test status', 'contact@contact.com']
        create_work_request(row)
    assert "Invalid data type provided" in str(e.value)

def test_create_work_request_invalid_value():
    with pytest.raises(ValueError) as e:
        row = ['ER-1234', 'valid', 'test description', 'high', 'test status']
        create_work_request(row)
    assert "Invalid number of arguments" in str(e.value)

def test_save_log_writes_report_content(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    valid = [work_request("1", "Fix pump", "desc", "High", "open", "a@b.com")]
    report = run_report(valid, [])
    report.save_log()

    content = (tmp_path / "run_report.log").read_text(encoding="utf-8")
    assert "Invalid Requests:" not in content
    assert "1 Valid Requests" in content
    assert "Fix pump" in content
