from __future__ import annotations

import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from .app import create_app
from .review import ReviewSession


def frontend_environment(api_origin: str) -> dict:
    url = urlsplit(api_origin)
    if (url.scheme != 'http' or url.hostname != '127.0.0.1' or not url.port or url.path
            or url.query or url.fragment or url.username):
        raise ValueError('frontend needs an explicit loopback review API origin')
    allowed = {'PATH', 'PATHEXT', 'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'USERPROFILE', 'APPDATA',
               'LOCALAPPDATA', 'HOME', 'HOMEDRIVE', 'HOMEPATH', 'TEMP', 'TMP', 'TMPDIR'}
    result = {key: value for key, value in os.environ.items() if key.upper() in allowed}
    result.update(NEXT_TELEMETRY_DISABLED='1', BINTANONG_REVIEW_API_ORIGIN=api_origin)
    return result


def _frontend(root: Path, env: dict, log) -> tuple[str, Path]:
    node = shutil.which('node')
    if node is None:
        raise ValueError('Node is not installed; no automatic installation is performed')
    if any(root.glob('.env*')):
        raise ValueError('remove environment files from the isolated researcher app; credentials are not accepted')
    declared = json.loads((root / 'package.json').read_bytes())
    for name, version in (declared['dependencies'] | declared['devDependencies']).items():
        path = root / 'node_modules' / name / 'package.json'
        if not path.is_file() or json.loads(path.read_bytes())['version'] != version:
            raise ValueError(f'link the approved existing node_modules with {name}@{version}; installs are disabled')
    actual = subprocess.check_output([node, '--version'], text=True).strip().lstrip('v')
    if actual != declared['engines']['node']:
        print(f'Runtime disclosure: installed Node {actual}; project target is {declared["engines"]["node"]}.', file=sys.stderr)
    fingerprint = hashlib.sha256(env['BINTANONG_REVIEW_API_ORIGIN'].encode())
    files = [root / name for name in ('package.json', 'tsconfig.json', 'next.config.mjs', 'postcss.config.mjs', 'proxy.ts')]
    for folder in ('app', 'components', 'lib'):
        files.extend(p for p in (root / folder).rglob('*') if p.is_file())
    for path in sorted(files):
        fingerprint.update(path.relative_to(root).as_posix().encode())
        fingerprint.update(path.read_bytes())
    marker = root / 'audit-evidence/source.sha256'
    next_cli = root / 'node_modules/next/dist/bin/next'
    if (not (root / 'audit-evidence/next/BUILD_ID').exists()
            or not marker.exists() or marker.read_text() != fingerprint.hexdigest()):
        result = subprocess.run([node, str(next_cli), 'build', '--webpack', str(root)],
            cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            raise ValueError('researcher frontend build failed; inspect the local runtime log')
        marker.parent.mkdir(exist_ok=True)
        marker.write_text(fingerprint.hexdigest())
    return node, next_cli


def serve(root: Path, reviewer: str, *, api_port: int = 8765, ui_port: int = 3001,
          open_browser: bool = True) -> None:
    if (any(type(p) is not int or not 1 <= p <= 65535 for p in (api_port, ui_port))
            or api_port == ui_port):
        raise ValueError('choose two distinct explicit local ports')
    import uvicorn
    api_origin, ui_origin = f'http://127.0.0.1:{api_port}', f'http://127.0.0.1:{ui_port}'
    app_root = Path(__file__).resolve().parents[3] / 'researcher'
    child = None
    server = None
    worker = None
    with ReviewSession(root, reviewer) as session:
        runtime = session.root / 'review/runtime'
        runtime.mkdir(parents=True, exist_ok=True)
        temporary = runtime / 'tmp'
        temporary.mkdir(exist_ok=True)
        env = frontend_environment(api_origin)
        env.update(TEMP=str(temporary), TMP=str(temporary), TMPDIR=str(temporary))
        token = secrets.token_urlsafe(32)
        try:
            with (runtime / 'frontend.log').open('a', encoding='utf-8') as log:
                node, next_cli = _frontend(app_root, env, log)
                server = uvicorn.Server(uvicorn.Config(create_app(session, token, port=api_port, ui_origin=ui_origin),
                    host='127.0.0.1', port=api_port, access_log=False, log_level='warning'))
                worker = threading.Thread(target=server.run, daemon=True)
                worker.start()
                until = time.monotonic() + 15
                while not server.started:
                    if not worker.is_alive() or time.monotonic() > until:
                        raise ValueError('review API could not start; choose an unused local port')
                    time.sleep(.05)
                child = subprocess.Popen([node, str(next_cli), 'start', str(app_root), '--hostname', '127.0.0.1',
                    '--port', str(ui_port)], cwd=app_root, env=env, stdout=log, stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                until = time.monotonic() + 30
                while True:
                    if child.poll() is not None or time.monotonic() > until:
                        raise ValueError('local researcher frontend did not start; inspect its runtime log')
                    try:
                        with urllib.request.urlopen(ui_origin, timeout=.5) as response:
                            if response.status == 200:
                                break
                    except (urllib.error.URLError, TimeoutError):
                        time.sleep(.1)
                link = ui_origin + '/#' + urlencode({'api': api_origin, 'token': token})
                print('Local researcher review: ' + link, flush=True)
                print('Keep this command running. Ctrl+C closes this review session.', flush=True)
                if open_browser:
                    webbrowser.open(link)
                while child.poll() is None:
                    time.sleep(.25)
        except KeyboardInterrupt:
            pass
        finally:
            if child is not None and child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
            if server is not None:
                server.should_exit = True
            if worker is not None:
                worker.join(timeout=10)
