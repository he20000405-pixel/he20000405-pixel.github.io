"""Build the five source snapshots with the same official Pages image.

Only the caller's candidate snapshot is eligible for deployment. Other repositories
are fixed to the main SHA fetched at the start, for offline cross-site validation.
No personal token or third-party service is required.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

OWNER = 'he20000405-pixel'
REPOS = {
    'portal': 'he20000405-pixel.github.io',
    'chatgpt': 'chatgpt-plus-pro-china-guide',
    'grok': 'supergrok-china-guide',
    'claude': 'claude-pro-max-china-guide',
    'gemini': 'gemini-google-ai-pro-china-guide',
}
IMAGE = 'ghcr.io/actions/jekyll-build-pages@sha256:6791ebfd912185ed59bfb5fb102664fa872496b79f87ff8b9cfba292a7345041'

def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)

def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args], text=True).strip()

def xml_value(node):
    children = [xml_value(c) for c in node]
    if node.tag.endswith('}urlset'):
        children.sort(key=lambda c: json.dumps(c, sort_keys=True))
    return [node.tag, sorted(node.attrib.items()), (node.text or '').strip(), children]

def manifest(root):
    result = {}
    for file in sorted(root.rglob('*')):
        if not file.is_file():
            continue
        data = file.read_bytes()
        value = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
        if file.suffix in {'.html', '.css', '.js', '.json', '.xml', '.txt', '.svg'}:
            value['lfSha256'] = hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest()
        if file.name == 'sitemap.xml':
            value['xmlSha256'] = hashlib.sha256(json.dumps(xml_value(ET.fromstring(data)), ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        result[file.relative_to(root).as_posix()] = value
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repository', required=True)
    parser.add_argument('--expected-sha', required=True)
    args = parser.parse_args()
    if args.repository not in {OWNER + '/' + name for name in REPOS.values()}:
        parser.error('Only the five configured public knowledge repositories are supported')
    workspace = Path.cwd().resolve()
    sources = workspace / 'sources'
    evidence = workspace / 'evidence'
    evidence.mkdir(exist_ok=True)
    snapshots = {}
    current_alias = None
    # Fetch each dependency once; builds use these immutable local snapshots.
    for alias, name in REPOS.items():
        path = sources / name
        is_current = args.repository == OWNER + '/' + name
        if is_current:
            current_alias = alias
            if not path.is_dir() or git(path, 'rev-parse', 'HEAD') != args.expected_sha:
                raise RuntimeError('Candidate checkout does not match the workflow SHA')
        else:
            if path.exists():
                raise RuntimeError('Unexpected preexisting dependency directory: ' + str(path))
            run('git', 'clone', '--depth', '1', '--branch', 'main', '--single-branch',
                'https://github.com/' + OWNER + '/' + name + '.git', str(path))
        snapshots[alias] = {'repository': OWNER + '/' + name,
                            'sha': git(path, 'rev-parse', 'HEAD'),
                            'candidate': is_current}
    (evidence / 'source-snapshots.json').write_text(json.dumps(snapshots, indent=2), encoding='utf-8')
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
        output.write('current_alias=' + current_alias + '\n')
    run('docker', 'pull', IMAGE)
    (evidence / 'build-image.txt').write_text(IMAGE + '\n', encoding='utf-8')
    # Override the image entrypoint, NOT GitHub's reserved environment variables.
    # The stock action always uses the triggering repo's identity, which is wrong
    # for the other four sites. Use each snapshot's own metadata and revision.
    for alias, name in REPOS.items():
        print('::group::Build ' + name, flush=True)
        run('docker', 'run', '--rm',
            '--volume', str(workspace) + ':/github/workspace',
            '--workdir', '/usr/local/bundle',
            '--env', 'JEKYLL_ENV=production',
            '--env', 'PAGES_REPO_NWO=' + OWNER + '/' + name,
            '--env', 'JEKYLL_BUILD_REVISION=' + snapshots[alias]['sha'],
            '--env', 'PAGES_API_URL=https://api.github.com',
            '--env', 'JEKYLL_GITHUB_TOKEN',
            '--entrypoint', '/usr/local/bundle/bin/github-pages', IMAGE,
            'build', '--source', '/github/workspace/sources/' + name,
            '--destination', '/github/workspace/build/' + alias)
        print('::endgroup::', flush=True)
    (evidence / 'build-manifest.json').write_text(json.dumps(manifest(workspace / 'build'), indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
