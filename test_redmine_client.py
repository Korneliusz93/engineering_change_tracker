import pytest
from redminelib import Redmine
from redminelib.resultsets import ResourceSet
from redminelib.resources import Issue
from main import CustomField
from redmine_client import redmine_client

from dotenv import load_dotenv
load_dotenv()
import requests
import os

api_key = os.getenv("REDMINE_API_KEY")

load_dotenv()
redmine = Redmine( "http://localhost:3000/", key=api_key)

def test_api_key_directly():

    import os
    import requests
    api_key = os.getenv("REDMINE_API_KEY")
    response = requests.get(
        "http://localhost:3000/users/current.json",
        headers={"X-Redmine-API-Key": api_key}
    )
    print("Key exists:", api_key is not None)
    print("Key length:", len(api_key) if api_key else 0)
    print("HTTP status:", response.status_code)
    print("Response:", response.text)

    assert response.status_code == 200

def test_redmine_current_user():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine, test_project)
    engine = rc.redmine.engine
    print("Configured API key:", bool(engine.requests['headers'].get('X-Redmine-API-Key')))
    print("Configured key length:", len(engine.requests['headers'].get('X-Redmine-API-Key', '')))
    user = rc.redmine.user.get('current')
    print("Authenticated user:", user.login)

def test_get_projects():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine, test_project)
    projects = rc.get_projects()
    assert isinstance(projects, list)
    assert len(projects) > 0

#TEST Project
#test-redmine-connection
def test_get_issues():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine,test_project)
    issues = rc.get_issues()
    assert isinstance(issues, list)
    assert len(issues) > 0

def test_get_issue():
    id = 1
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine, test_project)
    issue = rc.get_issue(id)
    print(issue)
    assert issue is not None
    assert isinstance(issue, dict)

def test_get_roles():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine, test_project)
    roles = rc.get_roles()
    assert isinstance(roles, list)
    assert len(roles) > 0

def test_get_memberships():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine, test_project)
    memberships = rc.get_memberships()
    assert isinstance(memberships, list)

def test_priorities():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine, test_project)
    priorities = rc.redmine.enumeration.filter(resource='issue_priorities')
    assert priorities is not None
    assert isinstance(priorities, ResourceSet)
    assert len(priorities) > 0

def test_custom_fields():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine, test_project)
    custom_fields = rc.get_custom_fields()
    assert isinstance(custom_fields, list)
    assert custom_fields is not None
    assert len(custom_fields) > 0

def test_create_issue():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine, test_project)
    issue = rc.create_issue('Update power supply module','Replace component with revised version','Low', "new", [{"id":2,"value":"a@b.pl"}])
    assert isinstance(issue, Issue)
    assert issue is not None