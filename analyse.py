import json
import re
from datetime import datetime
from itertools import groupby
from typing import Callable

from mappings import mapping


def read_json(file_path='a:\git_status\git_status.json'):
    with open(file_path, 'r', encoding='utf-8') as fi:
        return json.load(fi)


def parse_branches(json_data, period_aggregator: Callable):
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
        repo['profile'] = {k: len(list(v)) for k, v in groupby(
            sorted([v for b in repo['parsed_branches'].values() for v in b], key=period_aggregator),
            period_aggregator)}
        repo['folder_name'] = repo['folder'].split('\\')[-1]
        repo['name'] = (repo['remote'].replace('/ (push)', '').split('/')[-1].replace('(push)', '').strip()
                        if repo['remote'] and isinstance(repo['remote'], str)
                        else repo['remote'][0].split('/')[-1].replace('(push)', '').strip()
        if repo['remote'] and isinstance(repo['remote'], list)
        else repo['folder_name'])
    return json_data


# (groupby(sorted(((j, mapping.get(j['name'], j['name'])) for j in json_data), key=lambda j:j[1]) , lambda x:x[1]))
# list(groupby(sorted(((j, mapping.get(j['name'], j['name'])) for j in json_data), key=lambda j:j[1]) , lambda x:x[1]))
# list((k, [vv[0] for vv in v]) for k, v in groupby(sorted(((j, mapping.get(j['name'], j['name']).capitalize()) for j in json_data), key=lambda j:j[1]) , lambda x:x[1]))

def aggregate_projects(json_data, mapping: dict):
    projects = {k: v
                for k, v
                in sorted(((k,
                            {d: sum((cc[1] for cc in c))
                             for d, c in groupby([i for profile in v
                                                  for i in profile['profile'].items()],
                                                 lambda x: x[0])})
                           for k, v in ((k, [vv[0] for vv in v]) for k, v in groupby(
            sorted(((j, mapping.get(j['name'], j['name']).capitalize()) for j in json_data), key=lambda j: j[1]),
            lambda x: x[1]))),
                          key=lambda x: x[0])
                if v}

    return projects


def build_md(json_data):
    dates = set((mth for repo in json_data for mth in repo['profile'].keys()))
    md = ' | ' + ' |\n| '.join([
                                   ' | '.join(['Repository', 'Folder'] + sorted(dates)),
                                   ' | '.join(['---'] * (len(dates) + 2))
                               ]
                               + [
                                   ' | '.join(
                                       [repo['name'], repo['folder_name']] + [str(repo['profile'].get(mth, '')) for mth
                                                                              in dates])
                                   for repo in sorted(json_data, key=lambda x: x['name'])])

    return md


def build_md_from_agged(json_data):
    dates = set((mth for repo in json_data.values() for mth in repo.keys()))
    md = ' | ' + ' |\n| '.join([
                                   ' | '.join(['Repository'] + sorted(dates)),
                                   ' | '.join(['---'] * (len(dates) + 1))
                               ]
                               + [
                                   ' | '.join(
                                       [k] + [str(v.get(mth, '')) for mth in dates])
                                   for k, v in json_data.items()])

    return md


# build stats

month_aggregator = lambda x: x['datetime'].strftime('%Y-%m')
quarter_aggregator = lambda x: x['datetime'].strftime('%Y') + 'Q' + str((x['datetime'].month - 1) // 3 + 1)
year_aggregator = lambda x: x['datetime'].strftime('%Y')

data = parse_branches(read_json(), year_aggregator)
dumps = json.dumps(data, indent=2, default=str)
with open('a:\git_status\git_status_parsed.json', 'w', encoding='utf-8') as fo:
    fo.write(dumps)
print(dumps)

with open('a:\git_status\git_status_parsed.md', 'w', encoding='utf-8') as fo:
    fo.write(build_md(data))

aggregated = aggregate_projects(data, mapping)
with open('a:\git_status\git_status_aggregated.json', 'w', encoding='utf-8') as fo:
    fo.write(json.dumps(aggregated, indent=2, default=str))
# print(json.dumps({k: k for k in sorted((k for k in aggregated.keys()))}, indent=2, default=str))
with open('a:\git_status\git_status_aggregated.md', 'w', encoding='utf-8') as fo:
    fo.write(build_md_from_agged(aggregated))
