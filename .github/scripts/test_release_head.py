"""Offline release-head tests: latest succeeds; stale/unknown must fail closed."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import check_release_head as guard


REPO = 'he20000405-pixel/he20000405-pixel.github.io'
CURRENT = 'a' * 40
OLDER = 'b' * 40


class Response(io.BytesIO):
    status = 200


class Client:
    def __init__(self, body=None, error=None, status=200):
        self.body = body if body is not None else json.dumps({
            'ref': 'refs/heads/main', 'object': {'type': 'commit', 'sha': CURRENT},
        }).encode()
        self.error, self.status, self.requests = error, status, []

    def open(self, request, timeout):
        self.requests.append((request, timeout))
        if self.error:
            raise self.error
        result = Response(self.body)
        result.status = self.status
        return result


class ReleaseHeadTests(unittest.TestCase):
    def test_current_candidate_succeeds_with_read_only_exact_ref(self):
        client = Client()
        result = guard.check_release(REPO, CURRENT, 'fixture-token', client)
        self.assertTrue(result['passed'])
        self.assertEqual(result['currentMainSHA'], CURRENT)
        request, timeout = client.requests[0]
        self.assertEqual(request.get_method(), 'GET')
        self.assertEqual(request.full_url, 'https://api.github.com/repos/' + REPO + '/git/ref/heads/main')
        self.assertEqual(request.headers['Authorization'], 'Bearer fixture-token')
        self.assertEqual(timeout, 20)
        self.assertNotIn('fixture-token', json.dumps(result))

    def test_stale_candidate_cannot_deploy(self):
        result = guard.check_release(REPO, OLDER, opener=Client())
        self.assertFalse(result['passed'])
        self.assertEqual(result['currentMainSHA'], CURRENT)
        self.assertIn('no longer', result['error'])

    def test_http_errors_fail_closed(self):
        for status in (301, 401, 403, 404, 429, 500):
            with self.subTest(status=status):
                error = HTTPError('https://api.github.com/', status, 'failure', {}, None)
                result = guard.check_release(REPO, CURRENT, opener=Client(error=error))
                self.assertFalse(result['passed'])
                self.assertIn(str(status), result['error'])

    def test_network_failure_and_timeout_fail_closed(self):
        for error in (URLError('unavailable'), TimeoutError('timeout'), OSError('network')):
            with self.subTest(error=type(error).__name__):
                result = guard.check_release(REPO, CURRENT, opener=Client(error=error))
                self.assertFalse(result['passed'])
                self.assertIsNone(result['currentMainSHA'])

    def test_bad_response_cannot_be_treated_as_current_main(self):
        values = [None, [], {}, {'ref': 'refs/heads/other'},
                  {'ref': 'refs/heads/main', 'object': {'type': 'tag', 'sha': CURRENT}},
                  {'ref': 'refs/heads/main', 'object': {'type': 'commit', 'sha': 'abc'}},
                  {'ref': 'refs/heads/main', 'object': {'type': 'commit', 'sha': 123}}]
        for value in values:
            with self.subTest(value=value):
                result = guard.check_release(REPO, CURRENT, opener=Client(json.dumps(value).encode()))
                self.assertFalse(result['passed'])
        for raw in (b'<html>error</html>', b'\xff', b'x' * (1024 * 1024 + 1)):
            self.assertFalse(guard.check_release(REPO, CURRENT, opener=Client(raw))['passed'])

    def test_non_200_status_fails_closed(self):
        self.assertFalse(guard.check_release(REPO, CURRENT, opener=Client(status=204))['passed'])

    def test_invalid_input_never_calls_api(self):
        for repository, candidate in ((REPO, 'main'), (REPO, ''), ('other/repo', CURRENT),
                                      ('he20000405-pixel/../other', CURRENT)):
            with self.subTest(repository=repository, candidate=candidate):
                client = Client()
                self.assertFalse(guard.check_release(repository, candidate, opener=client)['passed'])
                self.assertEqual(client.requests, [])

    def test_redirect_is_never_followed(self):
        self.assertIsNone(guard.NoRedirect().redirect_request(None, None, 301, '', {}, 'https://elsewhere.example'))

    def test_cli_exit_code_and_report(self):
        for candidate, expected_code in ((CURRENT, 0), (OLDER, 1)):
            with tempfile.TemporaryDirectory() as directory:
                report = Path(directory) / 'evidence' / 'head.json'
                with patch.object(guard, 'build_opener', return_value=Client()), contextlib.redirect_stdout(io.StringIO()):
                    code = guard.main(['--repository', REPO, '--candidate-sha', candidate, '--report', str(report)])
                self.assertEqual(code, expected_code)
                data = json.loads(report.read_text(encoding='utf-8'))
                self.assertEqual(data['passed'], expected_code == 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
