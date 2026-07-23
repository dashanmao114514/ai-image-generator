import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get('API_KEY', '')
BASE_URL = 'https://api.lk888.ai/api'

HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}


@app.route('/api/generate', methods=['POST'])
def generate():
    """提交图片生成任务"""
    body = request.json
    if not body or not body.get('model') or not body.get('prompt'):
        return jsonify({'error': '缺少 model 或 prompt 参数'}), 400

    try:
        resp = requests.post(
            f'{BASE_URL}/v1/media/generate',
            json=body,
            headers=HEADERS,
            timeout=60
        )
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.Timeout:
        return jsonify({'error': '请求上游超时'}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 502


@app.route('/api/status', methods=['GET'])
def task_status():
    """轮询任务状态"""
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({'error': '缺少 task_id'}), 400

    try:
        resp = requests.get(
            f'{BASE_URL}/v1/skills/task-status?task_id={task_id}',
            headers=HEADERS,
            timeout=30
        )
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 502


@app.route('/api/models', methods=['GET'])
def list_models():
    """获取模型列表（用于前端动态加载）"""
    model_type = request.args.get('type', 'image')
    try:
        resp = requests.get(
            f'{BASE_URL}/v1/skills/models?type={model_type}',
            headers=HEADERS,
            timeout=15
        )
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 502


@app.route('/api/balance', methods=['GET'])
def check_balance():
    """查询余额"""
    try:
        resp = requests.get(
            f'{BASE_URL}/v1/skills/balance',
            headers=HEADERS,
            timeout=15
        )
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 502


# Vercel Python 需要这个变量
app = app
