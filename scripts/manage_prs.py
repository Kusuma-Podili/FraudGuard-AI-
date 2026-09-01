"""Manage GitHub Pull Requests for FraudGuard-AI."""

import urllib.request
import urllib.error
import json
import subprocess

def get_github_token() -> str:
    p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, _ = p.communicate('protocol=https\nhost=github.com\n\n')
    for line in out.splitlines():
        if line.startswith('password='):
            return line.split('=', 1)[1]
    return ""

def list_pull_requests():
    token = get_github_token()
    req = urllib.request.Request(
        'https://api.github.com/repos/Kusuma-Podili/FraudGuard-AI-/pulls?state=all',
        headers={
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'FraudGuard-Agent'
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"Total PRs found: {len(data)}")
            for pr in data:
                print(f"PR #{pr['number']}: {pr['title']} | State: {pr['state']} | Merged: {pr.get('merged_at') is not None}")
            return data
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return []

if __name__ == "__main__":
    list_pull_requests()
