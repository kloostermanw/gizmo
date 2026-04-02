from Commands.command import Command
from Lib.termcolor import colored
import git
import json
import re
import subprocess

class Branches(Command):

    def configure(self):
        self.name = "branches";
        self.description = "show local branches with GitHub issue/PR status.";

    def handle(self, args):
        repo = git.Repo(search_parent_directories=True)
        branches = sorted([h.name for h in repo.heads])

        prs = self.fetchPRs()
        pr_by_branch = {}
        for pr in prs:
            pr_by_branch[pr['headRefName']] = pr

        rows = []
        for branch in branches:
            issue_state = ''
            pr_state = ''
            reviewers = ''

            match = re.match(r'^feature/issue-(\d+)', branch)
            project_name = ''
            project_status = ''

            if match:
                issue_number = match.group(1)
                issue = self.fetchIssue(issue_number)
                if issue:
                    issue_state = issue.get('state', '')
                    project_name, project_status = self.extractProject(issue)

            pr_number = ''
            pr = pr_by_branch.get(branch)
            if pr:
                pr_number = '#' + str(pr.get('number', ''))
                pr_state = pr.get('state', '')
                reviewers = self.formatReviewers(pr)

            rows.append((branch, issue_state, pr_number, pr_state, reviewers, project_name, project_status))

        self.printTable(rows, prs)

    def fetchPRs(self):
        try:
            result = subprocess.run(
                ['gh', 'pr', 'list', '--state', 'all', '--json', 'number,headRefName,state,latestReviews,reviewRequests', '-L', '100'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
            )
            if result.returncode == 0:
                return json.loads(result.stdout.decode('utf-8'))
        except FileNotFoundError:
            pass
        return []

    def fetchIssue(self, number):
        try:
            result = subprocess.run(
                ['gh', 'issue', 'view', str(number), '--json', 'state,assignees,projectItems'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
            )
            if result.returncode == 0:
                return json.loads(result.stdout.decode('utf-8'))
        except FileNotFoundError:
            pass
        return None

    def extractProject(self, issue):
        items = issue.get('projectItems', [])
        if items:
            first = items[0]
            name = first.get('project', {}).get('title', '') if isinstance(first.get('project'), dict) else first.get('title', '')
            status = first.get('status', {}).get('name', '') if isinstance(first.get('status'), dict) else ''
            return name, status
        return '', ''

    def formatReviewers(self, pr):
        reviewers = {}

        for req in pr.get('reviewRequests', []):
            login = req.get('login', '')
            if login and login not in reviewers:
                reviewers[login] = 'PENDING'

        for review in pr.get('latestReviews', []):
            login = review.get('author', {}).get('login', '')
            state = review.get('state', '')
            if login and state:
                reviewers[login] = state

        parts = []
        for login, state in reviewers.items():
            parts.append(login + ':' + state)

        return ', '.join(parts)

    def colorReviewers(self, pr):
        reviewers = {}

        for req in pr.get('reviewRequests', []):
            login = req.get('login', '')
            if login and login not in reviewers:
                reviewers[login] = 'PENDING'

        for review in pr.get('latestReviews', []):
            login = review.get('author', {}).get('login', '')
            state = review.get('state', '')
            if login and state:
                reviewers[login] = state

        review_colors = {
            'APPROVED': 'green',
            'CHANGES_REQUESTED': 'red',
            'COMMENTED': 'yellow',
            'PENDING': 'grey',
        }

        parts = []
        for login, state in reviewers.items():
            color = review_colors.get(state, 'white')
            parts.append(colored(login, 'cyan') + ':' + colored(state, color))

        return ', '.join(parts)

    def colorState(self, state):
        colors = {
            'OPEN': 'green',
            'CLOSED': 'red',
            'MERGED': 'magenta',
        }
        color = colors.get(state)
        if color:
            return colored(state, color)
        return state

    def colorProjectStatus(self, status):
        colors = {
            'Done': 'green',
            'In Progress': 'yellow',
            'In Review': 'cyan',
            'Todo': 'white',
        }
        color = colors.get(status, 'white')
        return colored(status, color)

    def printTable(self, rows, prs):
        headers = ('branch', 'issue', 'pr', 'status', 'reviewers', 'project', 'proj status')
        padding = 2

        widths = [len(h) for h in headers]
        for row in rows:
            for i, val in enumerate(row):
                widths[i] = max(widths[i], len(val))

        widths = [w + padding for w in widths]

        header_line = ''.join(colored(h.ljust(widths[i]), 'green') for i, h in enumerate(headers))
        separator = colored(''.join('-' * (w - padding) + ' ' * padding for w in widths), 'grey')

        print(header_line)
        print(separator)

        pr_by_branch = {pr['headRefName']: pr for pr in prs}

        for branch, issue_state, pr_number, pr_state, reviewers_plain, project_name, project_status in rows:
            pr = pr_by_branch.get(branch)
            cols = [
                colored(branch.ljust(widths[0]), 'white'),
                self.colorState(issue_state.ljust(widths[1])) if issue_state else ' ' * widths[1],
                colored(pr_number.ljust(widths[2]), 'white') if pr_number else ' ' * widths[2],
                self.colorState(pr_state.ljust(widths[3])) if pr_state else ' ' * widths[3],
                (self.colorReviewers(pr) + ' ' * (widths[4] - len(reviewers_plain))) if pr and reviewers_plain else ' ' * widths[4],
                colored(project_name.ljust(widths[5]), 'cyan') if project_name else ' ' * widths[5],
                self.colorProjectStatus(project_status) if project_status else '',
            ]
            print(''.join(cols).rstrip())
