import logging

from redminelib.exceptions import AuthError, BaseRedmineError, ServerError, ResourceNotFoundError


class redmine_client:
    def __init__(self, redmine):
        self.redmine = redmine
        self.project_id = ""
        self.project_name = ""

    def get_projects(self):
        projects = self.redmine.project.all()
        project_list = []
        for project in projects:
            project_list.append((project.name, project.identifier))
        return project_list

    def get_issues(self, project_id):
        issues = self.redmine.issue.filter(project_id=project_id)
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

    def get_memberships(self, project_id):
        memberships_list = []
        memberships = self.redmine.project_membership.filter(
            project_id=project_id
        )
        for membership in memberships:
            memberships_list.append(membership.user)
        return memberships_list

    def create_issue(self, subject, description, priority, status, project_id):
        try:
            issue = self.redmine.issue.create(
                project_id=project_id,
                subject=subject,
                status=status,
                description=description,
                priority=priority
            )
            return issue
        except AuthError as e:
            logging.error(e)
            raise AuthError()
        except ServerError as e:
            logging.error(e)
            raise ServerError()
        except ResourceNotFoundError as e:
            logging.error(e)
            raise ResourceNotFoundError()