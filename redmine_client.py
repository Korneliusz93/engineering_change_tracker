import logging

from redminelib.exceptions import AuthError, BaseRedmineError, ServerError, ResourceNotFoundError
from typing import List

class redmine_client:
    def __init__(self, redmine, project_id):
        self.redmine = redmine
        self.project_id = project_id

    def get_projects(self):
        projects = self.redmine.project.all()
        project_list = []
        for project in projects:
            project_list.append((project.name, project.identifier))
        return project_list

    def get_issues(self):
        issues = self.redmine.issue.filter(project_id=self.project_id)
        issue_list = []
        for issue in issues:
            issue_list.append((issue.id, issue.subject))
        return issue_list

    def get_issue(self, issue_id):
        issue = self.redmine.issue.get(issue_id)
        return issue.raw()

    def get_roles(self):
        roles = self.redmine.role.all()
        role_list = []
        for role in roles:
            role_list.append((role.id, role.name))
        return role_list

    def get_memberships(self):
        memberships_list = []
        memberships = self.redmine.project_membership.filter(
            project_id= self.project_id
        )
        for membership in memberships:
            memberships_list.append(membership.user)
        return memberships_list

    def get_custom_fields(self):
        custom_fields = self.redmine.custom_field.all()#.filter(project_id=self.project_id)
        custom_list = []
        for custom_field in custom_fields:
            custom_list.append((custom_field.id, custom_field.name))
        print(custom_list)
        return custom_list

    def create_issue(self, subject, description, priority, status, custom_fields):
        if custom_fields:
            return self.redmine.issue.create(
                project_id= self.project_id,
                subject=subject,
                status=status,
                description=description,
                priority=priority,
                custom_fields=custom_fields
            )
        else:
            return self.redmine.issue.create(
                project_id=self.project_id,
                subject=subject,
                status=status,
                description=description,
                priority=priority,
            )