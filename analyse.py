import json
import re
from datetime import datetime
from itertools import groupby


def read_json(file_path='a:\git_status.json'):
    with open(file_path, 'r', encoding='utf-8') as fi:
        return json.load(fi)


def parse_branches(json_data):
    re_branch = re.compile(r'^.*(?P<hash>[0-9a-f]{6,}) (?P<datetime>\d\d-\d\d-\d\d \d\d:\d\d) \[.+]\ (?P<commit>.*$)')

    for repo in json_data:
        # remove redundant branches, favor remote branches which have been updated by a fetch
        remote_branches = set([b.split('/')[-1] for b in repo['branches'].keys() if b[:8] != 'remotes/'])
        branches = {k: v for k, v in repo['branches'].items() if k[:8] == 'remotes/' or k not in remote_branches}
        parsed_branches = {}
        # parse commits
        repo['parsed_branches'] = {
            branch.split('/')[-1]:
                [{k: datetime.strptime(v, '%y-%m-%d %H:%M') if k == 'datetime' else v
                  for k, v in ma.groupdict().items()}
                 for ma in [re_branch.match(c) for c in commits] if ma is not None]
            for branch, commits in branches.items()
        }
        repo['profile'] = {k: len(list(v)) for k, v in groupby([v for b in repo['parsed_branches'].values() for v in b],
                                                               lambda x: x['datetime'].strftime('%Y-%m'))}
        repo['name'] = (repo['remote'].split('/')[-1].replace('(push)', '').strip()
                        if repo['remote'] and isinstance(repo['remote'], str)
                        else repo['remote'][0].split('/')[-1].replace('(push)', '').strip()
                        if repo['remote'] and isinstance(repo['remote'], list)
                        else repo['folder'][0].split('\\')[-1])
    return json_data


def build_md(json_data):
    dates = set((mth for repo in json_data for mth in repo['profile'].keys()))
    md = '|' + '|\n|'.join([
                               '|'.join(['Repository|'] + sorted(dates)),
                               '|'.join(['---'] * (len(dates) + 1))
                           ]
                           + [
                               '|'.join([repo['name'] + '|'] + [str(repo['profile'].get(mth, '')) for mth in dates])
                               for repo in json_data])

    return md


# build stats

data = parse_branches(read_json())
dumps = json.dumps(data, indent=2, default=str)
with open('a:\git_status_parsed.json', 'w', encoding='utf-8') as fo:
    fo.write(dumps)
print(dumps)

with open('a:\git_status_parsed.md', 'w', encoding='utf-8') as fo:
    fo.write(build_md(data))
print(dumps)
