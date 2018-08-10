# github-graders.py
# Dan Wallach <dwallach@rice.edu>

# (Note: only works with Python3)

import requests
import re
import argparse
import sys
import random

from typing import List, TypeVar

# see installation and usage instructions in README.md
default_github_token = ["YOUR_TOKEN_HERE"]

# your GitHub "project" or "organization" in which all your students' work lives
default_github_project = ["YOUR_PROJECT_HERE"]  # e.g., "RiceComp215"

# the default search prefix, most commonly this is set from the command-line
default_prefix = [""]

# your graders, preferably their GitHub IDs (we'll ignore them if they've also checked out a copy of the assignment)
grader_list = ["alice", "bob", "charlie", "dorothy", "eve", "frank"]

# your own GitHub ID and/or anybody else who you wish to exclude from being graded
ignore_list = ["danwallach"]

# command-line argument processing

parser = argparse.ArgumentParser(description='Random assignment of graders to students')
parser.add_argument('--token',
                    nargs=1,
                    default=default_github_token,
                    help='GitHub API token')
parser.add_argument('--project',
                    nargs=1,
                    default=default_github_project,
                    help='GitHub project to scan, default: ' + default_github_project[0])
parser.add_argument('--prefix',
                    nargs=1,
                    default=default_prefix,
                    help='Prefix on projects to match (default: match all projects)')

args = parser.parse_args()

github_prefix = args.prefix[0]
github_project = args.project[0]
github_token = args.token[0]

# Python3's parametric type hints are ... a thing.
T = TypeVar('T')


def group_list_by_n(l: List[T], n: int) -> List[List[T]]:
    """
    Given a list of whatever type, divides it into a list of lists, each of which is n elements long,
    until the last one, having whatever is left.
    """
    if len(l) == 0:
        return []
    elif len(l) <= n:
        return [l]
    else:
        return [l[0:n]] + group_list_by_n(l[n:], n)


def student_name_from(repo_name: str) -> str:
    """
    Given a GitHub repo "name" (e.g., "comp215-week01-intro-2017-danwallach") return the username suffix at the
    end ("danwallach"). If it's not there, the result is an empty string ("").
    """
    m = re.search(github_prefix + "-(.*)$", repo_name)
    if not m:
        return ""  # something funny in the name, so therefore not matching
    else:
        return m.group(1)


def desired_user(name: str) -> bool:
    """
    Given a GitHub repo "name" (e.g., "comp215-week01-intro-2017-danwallach"), returns true or false if that
    project is something we're trying to grade now, based on the specified prefix as well as the list of graders
    (to be ignored) and the ignore-list (also to be ignored).
    """
    m = student_name_from(name)
    return m != "" \
           and name.startswith(github_prefix) \
           and name != github_prefix \
           and m not in grader_list \
           and m not in ignore_list


request_headers = {
    "User-Agent": "GitHubGraders/1.0",
    "Authorization": "token " + github_token,
}

all_repos_list = []

page_number = 1
sys.stderr.write('Getting repo list from GitHub')

# Painful "paging" process to read a list of repos from GitHub.
while True:
    sys.stderr.write('.')
    sys.stderr.flush()

    repos_page = requests.get('https://api.github.com/orgs/%s/repos?page=%d' %
                              (github_project, page_number), headers=request_headers)
    page_number = page_number + 1

    if repos_page.status_code != 200:
        sys.stderr.write("\nFailed to load repos from GitHub: %s\n" % repos_page.content)
        exit(1)

    repos_page_json = repos_page.json()

    if len(repos_page_json) == 0:
        sys.stderr.write(" Done.\n")
        break

    all_repos_list = all_repos_list + repos_page.json()

# Each repo in the list has the following fields that we care about:
#
# clone_url: starts with https, suitable for checking out from the command-line
#     (e.g., 'https://github.com/RiceComp215/comp215-week01-intro-2017-danwallach.git')
#
# ssh_url: starts with git@github.com (e.g., 'git@github.com:RiceComp215/comp215-week01-intro-2017-danwallach.git')
#
# name: the name of the repo itself (e.g., 'comp215-week01-intro-2017-danwallach')
#
# full_name: the project and repo (e.g., 'RiceComp215/comp215-week01-intro-2017-danwallach')

filtered_repo_list = [x for x in all_repos_list if desired_user(x['name'])]

# note: we're shuffling the graders, so different graders get lucky each week when the load isn't evenly divisible
# and, of course, we're shuffling the repos.
random.seed()
random.shuffle(filtered_repo_list)
random.shuffle(grader_list)

# inefficient, but correct
grading_groups = [[entry[i] for entry
                   in group_list_by_n(filtered_repo_list, len(grader_list))
                   if i < len(entry)]
                  for i in range(len(grader_list))]

grader_map = dict(zip(grader_list, grading_groups))

print("# Grade assignments for %s" % github_prefix)
print("%d repos are ready to grade\n" % len(filtered_repo_list))
for grader in sorted(grader_map.keys(), key=str.lower):
    print("## %s (%d total)" % (grader, len(grader_map[grader])))
    for repo in sorted(grader_map[grader], key=lambda x: str.lower(x['name'])):
        print("- [%s](%s)" % (student_name_from(repo['name']), 'https://github.com/%s' % repo['full_name']))
