"""Fail closed unless the validated candidate is still this repository's main.

This is a deployment-time freshness check, not another build. The workflow must
run it immediately before deploying the already validated artifact. It cannot
retroactively change old workflow definitions or make an API read and a Pages
deployment atomic.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener


REPOSITORIES = {
    'he20000405-pixel/' + name for name in (
        'he20000405-pixel.github.io', 'chatgpt-plus-pro-china-guide',
        'supergrok-china-guide', 'claude-pro-max-china-guide',
        'gemini-google-ai-pro-china-guide',
    )
}
SHA = re.compile(r'[0-9a-f]{40}')


class ReleaseHeadError(RuntimeError):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # A moved/deleted repository requires review, not forwarding the token.
        return None


def fetch_main(repository, token=None, opener=None):
    if repository not in REPOSITORIES:
        raise ReleaseHeadError('Repository is not one of the five configured knowledge bases')
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
        'User-Agent': 'ChongGrok-release-head-check',
        'Cache-Control': 'no-cache',
    }
    if token:
        headers['Authorization'] = 'Bearer ' + token
    request = Request('https://api.github.com/repos/' + repository + '/git/ref/heads/main',
                      headers=headers)
    client = opener or build_opener(NoRedirect())
    try:
        with client.open(request, timeout=20) as response:
            if response.status != 200:
                raise ReleaseHeadError('GitHub main lookup returned HTTP ' + str(response.status))
            data = response.read(1024 * 1024 + 1)
            if len(data) > 1024 * 1024:
                raise ReleaseHeadError('GitHub main lookup response is unexpectedly large')
            value = json.loads(data)
    except HTTPError as error:
        raise ReleaseHeadError('GitHub main lookup returned HTTP ' + str(error.code)) from None
    except (URLError, TimeoutError, OSError):
        raise ReleaseHeadError('Cannot confirm current main because the GitHub API request failed') from None
    except (ValueError, UnicodeError):
        raise ReleaseHeadError('GitHub main lookup did not return valid JSON') from None
    if not isinstance(value, dict) or value.get('ref') != 'refs/heads/main':
        raise ReleaseHeadError('GitHub main lookup returned an unexpected reference')
    obj = value.get('object')
    if not isinstance(obj, dict) or obj.get('type') != 'commit':
        raise ReleaseHeadError('GitHub main lookup did not identify a commit')
    current = obj.get('sha')
    if not isinstance(current, str) or not SHA.fullmatch(current):
        raise ReleaseHeadError('GitHub main lookup did not return a full commit SHA')
    return current


def check_release(repository, candidate_sha, token=None, opener=None):
    result = {
        'repository': repository,
        'candidateSHA': candidate_sha,
        'currentMainSHA': None,
        'checkedAt': datetime.now(timezone.utc).isoformat(),
        'passed': False,
    }
    try:
        if not SHA.fullmatch(candidate_sha):
            raise ReleaseHeadError('Candidate must be a full lowercase commit SHA')
        current = fetch_main(repository, token, opener)
        result['currentMainSHA'] = current
        if candidate_sha != current:
            raise ReleaseHeadError('Candidate is no longer the latest main commit; keep the current live site and run the latest main')
        result['passed'] = True
    except ReleaseHeadError as error:
        result['error'] = str(error)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--candidate-sha', required=True)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args(argv)
    result = check_release(args.repository, args.candidate_sha, os.environ.get('GH_TOKEN'))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
