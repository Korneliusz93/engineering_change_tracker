from operator import contains

import pytest
from main import WorkRequest, RunReport, create_work_request, CustomField

def test_validate_same_id():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'contact@contact.com'))
    id_list = {'ER-123'}
    assert wr.validate(id_list) == False
    assert "Id is already taken" in wr.log

def test_validate_title():
    wr = WorkRequest('ER-123', '', 'test description', 'test prio', 'test status', CustomField(2,'contact@contact.com'))
    assert wr.validate(set()) == False
    assert "Empty title" in wr.log

def test_validate_invalid_contact1():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'contact#contact.com'))
    assert wr.validate(set()) == False
    assert "Invalid contact" in wr.log

def test_validate_invalid_contact2():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'.b@sh.rc'))
    assert wr.validate(set()) == False
    assert "Invalid contact" in wr.log

def test_validate_invalid_contact3():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'example@test.c0'))
    assert wr.validate(set()) == False
    assert "Invalid contact" in wr.log

def test_validate_invalid_contact4():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'freecodecamp.org'))
    assert wr.validate(set()) == False
    assert "Invalid contact" in wr.log

def test_validate_invalid_contact5():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'hello.@wo.rld'))
    assert wr.validate(set()) == False
    assert "Invalid contact" in wr.log

def test_validate_invalid_contact6():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'hello@world..com'))
    assert wr.validate(set()) == False
    assert "Invalid contact" in wr.log

def test_validate_invalid_contact7():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'develop..ment_user@c0D!NG.R.CKS'))
    assert wr.validate(set()) == False
    assert "Invalid contact" in wr.log

def test_validate_invalid_contact8():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'it@commit@push.io'))
    assert wr.validate(set()) == False
    assert "Invalid contact" in wr.log

def test_validate_valid_contact1():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'a@b.cd'))
    assert wr.validate(set()) == False
    assert "Invalid contact" not in wr.log

def test_validate_valid_contact2():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'hell.-w.rld@example.com'))
    assert wr.validate(set()) == False
    assert "Invalid contact" not in wr.log

def test_validate_valid_contact3():
    wr = WorkRequest('ER-123', 'test title', 'test description', 'test prio', 'test status', CustomField(2,'develop.ment_user@c0D!NG.R.CKS'))
    assert wr.validate(set()) == False
    assert "Invalid contact" not in wr.log

def test_validate_work_request_invalid_request():
    wr = WorkRequest('ER-123', '', 'test description', 'super', 'test status', CustomField(2,'contact#contact.com'))
    req_ids = {'ER-123'}
    is_valid = wr.validate(req_ids)
    assert "Id is already taken" in wr.log
    assert "Empty title" in wr.log
    assert "Invalid priority" in wr.log
    assert "Invalid contact" in wr.log
    assert is_valid == False

def test_validate_work_request_invalid_id_list():
    wr = WorkRequest('ER-123', 'valid', 'test description', 'high', 'test status', CustomField(2,'contact@contact.com'))
    is_valid = wr.validate( 'ER-123')
    assert is_valid == False

def test_validate_work_request_invalid_id_list_type():
    wr = WorkRequest('ER-123', 'valid', 'test description', 'high', 'test status', CustomField(2,'contact@contact.com'))
    is_valid = wr.validate([23])
    assert is_valid == False

def test_validate_description_empty():
    wr = WorkRequest('ER-123', 'valid', '', 'high', 'test status', CustomField(2,'contact@contact.com'))
    is_valid = wr.validate({'ER-423'})
    assert is_valid == False

def test_validate_description_none():
    wr = WorkRequest('ER-123', 'valid', None, 'high', 'test status', CustomField(2,'contact@contact.com'))
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
    valid = [WorkRequest("1", "Fix pump", "desc", "High", "open", CustomField(2,'contact@contact.com'))]
    report = RunReport(valid, [])
    report.save_log()
    content = (tmp_path / "run_report.log").read_text(encoding="utf-8")
    assert "Invalid Requests:" not in content
    assert "1 Valid Requests" in content
    assert "Fix pump" in content
