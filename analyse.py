import json
import re
from datetime import datetime


def read_json(file_path='a:\git_status.json'):
    with open(file_path, 'r', encoding='utf-8') as fi:
        return json.load(fi)


re_branch = re.compile(r'^.*(?P<hash>[0-9a-f]{6,}) (?P<datetime>\d\d-\d\d-\d\d \d\d:\d\d) \[.+]\ (?P<commit>.*$)')

data = read_json()
for repo in data:
    # remove redundant branches, favor remote branches which have been updated by a fetch
    remote_branches = set([b.split('/')[-1] for b in repo['branches'].keys() if b[:8] != 'remotes/'])
    branches = {k: v for k, v in repo['branches'].items() if k[:8] == 'remotes/' or k not in remote_branches}
    parsed_branches = {}
    # parse commits
    repo['parsed_branches'] = {
        branch.split('/')[-1]:
            [{k: datetime.strptime(v, '%y-%m-%d %H:%M') if k=='datetime' else v
              for k, v in ma.groupdict().items()}
             for ma in [re_branch.match(c) for c in commits] if ma is not None]
        for branch, commits in branches.items()
    }
# build stats

dumps = json.dumps(data, indent=2, default=str)
with open('a:\git_status_parsed.json', 'w', encoding='utf-8') as fo:
    fo.write(dumps)
print(dumps)
