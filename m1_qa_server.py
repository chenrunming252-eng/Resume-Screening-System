"""Offline browser integration fixture. Never contacts DeepSeek."""
import io
import json
import os
import sys
from unittest.mock import patch

sys.path.insert(0, 'D:/codex-talkdata/2026-11-02/zhe/outputs/resume-c')
from app import app

os.environ['DEEPSEEK_API_KEY'] = 'offline-browser-fixture'


def fixture_transport(request, timeout):
    payload = json.loads(request.data)
    latest = payload['messages'][-1]['content']
    if latest == '模拟超时':
        raise TimeoutError()
    data = {
        'reply': '【离线验收替身，不是真实 AI 回复】已找到一条候选内容，请修改后确认。',
        'proposals': [{'section': 'projects', 'text': latest, 'evidence': latest}],
        'missing_fields': ['项目时间'],
    }
    return io.BytesIO(json.dumps({'choices': [{'finish_reason': 'stop', 'message': {
        'content': json.dumps(data, ensure_ascii=False)}}]}).encode())


with patch('deepseek_client.urlopen', side_effect=fixture_transport):
    app.run(host='127.0.0.1', port=5002, debug=False)
