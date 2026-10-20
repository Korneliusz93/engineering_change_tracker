from redminelib import Redmine
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
    rc = redmine_client(redmine)

    engine = rc.redmine.engine
    print("Configured API key:", bool(engine.requests['headers'].get('X-Redmine-API-Key')))
    print("Configured key length:", len(engine.requests['headers'].get('X-Redmine-API-Key', '')))

    user = rc.redmine.user.get('current')
    print("Authenticated user:", user.login)

def test_get_projects():
    rc = redmine_client(redmine)
    projects = rc.get_projects()
    assert isinstance(projects, list)

#TEST Project
#test-redmine-connection
def test_get_issues():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine)
    issues = rc.get_issues(test_project)
    assert isinstance(issues, list)

def test_get_issue():
    id = 1
    rc = redmine_client(redmine)
    issue = rc.get_issue(id)
    print(issue)
    assert isinstance(issue, dict)

def test_get_roles():
    rc = redmine_client(redmine)
    roles = rc.get_roles()
    assert isinstance(roles, list)

def test_get_memberships():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine)
    memberships = rc.get_memberships(test_project)
    assert isinstance(memberships, list)

def test_create_issue():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine)

    issue = rc.create_issue('Update power supply module','Replace component with revised version','Low', "new", test_project)
    assert isinstance(issue, dict)

    assert issue is not None

def test_priorities():
    test_project = 'test-redmine-connection'
    rc = redmine_client(redmine)
    priorities = rc.redmine.enumeration.filter(resource='issue_priorities')
    assert isinstance(priorities, list)