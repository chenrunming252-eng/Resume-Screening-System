"""Enter a key without echo; verify against official DeepSeek; start local app."""
import getpass
import json
import os
import pathlib
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

root = pathlib.Path('D:/codex-talkdata/2026-11-02/zhe/outputs/resume-c')
key = getpass.getpass('DeepSeek API Key (hidden): ').strip()
if not key:
    print('No key received.', flush=True)
    raise SystemExit(1)
try:
    with urlopen(Request('https://api.deepseek.com/models', headers={'Authorization': 'Bearer ' + key}), timeout=25) as response:
        models = [item['id'] for item in json.load(response)['data']]
except HTTPError as error:
    print(json.dumps({'step': 'models', 'status': error.code, 'authenticated': False}), flush=True)
    raise SystemExit(1) from None
except (URLError, TimeoutError, OSError):
    print('Official endpoint network connection failed.', flush=True)
    raise SystemExit(2) from None
model = next((item for item in ('deepseek-flash', 'deepseek-chat') if item in models), None)
if model is None:
    print(json.dumps({'step': 'models', 'available_models': models, 'model_selected': False}), flush=True)
    raise SystemExit(3)
target = root / '.env'
if target.exists():
    print('Local configuration already exists; refused to overwrite.', flush=True)
    raise SystemExit(4)
with target.open('x', encoding='utf-8') as config:
    config.write('DEEPSEEK_API_KEY=' + key + '\nDEEPSEEK_MODEL=' + model + '\n')
os.environ['DEEPSEEK_API_KEY'] = key
os.environ['DEEPSEEK_MODEL'] = model
del key
sys.path.insert(0, str(root))
from app import app
started = time.monotonic()
response = app.test_client().post('/api/chat', json={'messages': [{'role': 'user', 'content': '【虚构测试材料】课程项目是校园二手交易网站，使用 Python 和 MySQL，负责商品搜索接口。没有实习经历，没有用户量或性能测试数据。'}]})
result = response.get_json()
summary = {'step': 'real_chat', 'http_status': response.status_code, 'model': model, 'elapsed_seconds': round(time.monotonic()-started, 2), 'proposal_count': len(result.get('proposals', [])), 'error_code': result.get('code')}
print(json.dumps(summary, ensure_ascii=False), flush=True)
report = {'summary': summary, 'result': result, 'key_saved': 'ignored local .env; not in source or frontend'}
(root / 'docs' / 'deepseek-live-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
if response.status_code != 200:
    raise SystemExit(5)
print('Starting configured backend at http://127.0.0.1:5000', flush=True)
app.run(host='127.0.0.1', port=5000, debug=False)
