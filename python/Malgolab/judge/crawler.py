import re
import requests
import time
import json
from pathlib import Path
from bs4 import BeautifulSoup
from .models import add_problem

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
PROJECT_ROOT = Path(__file__).resolve().parents[3]
API_BASE = "https://codeforces.com/api"
CACHE_DIR = PROJECT_ROOT / 'data' / 'cache'
PROBLEMS_CACHE = CACHE_DIR / 'problemset.json'
CACHE_EXPIRY_DAYS = 1   # 缓存有效期（天），设为0则每次更新

# print(PROJECT_ROOT)

def get_cached_problems():
    '''
    get_cached_problems 的 Docstring
    获取缓存的题目列表，如果缓存不存在或过期则重新请求 API
    '''
    if PROBLEMS_CACHE.exists():
        mtime = PROBLEMS_CACHE.stat().st_mtime
        if time.time() - mtime < CACHE_EXPIRY_DAYS * 86400:
            try:
                with open(PROBLEMS_CACHE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except: 
                pass
        
    url = f"{API_BASE}/problemset.problems"   
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise RuntimeError(f"API返回失败：{e}")
    if data.get('status') != 'OK':
        raise RuntimeError(f"API返回错误：{data}")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROBLEMS_CACHE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return data

def fetch_cf_problem_meta(contest_id, problem_index):
    '''
    fetch_cf_problem_meta 的 Docstring
    通过 Codeforces 官方 API 获取题目元数据（标题、标签、难度）
    使用 problemset.problems 接口，该接口返回所有题目，需要遍历查找
    :param contest_id: 比赛编号
    :param problem_index: 题目索引
    '''
    
    data = get_cached_problems()

    for problem in data['result']['problems']:
        if problem.get('contestId') == contest_id and problem.get('index') == problem_index:
            return {
                'title': problem.get('name', ''),
                'tags': problem.get('tags', []),
                'rating': problem.get('rating', 0)
            }
    raise RuntimeError(f"未找到题目：{contest_id} {problem_index}")

def fetch_cf_samples(contest_id, problem_index):
    '''
    fetch_cf_problem 的 Docstring
    通过网页抓取获取样例、时间限制、内存限制
    :param contest_id: 比赛id
    :param problem_index: 题目索引
    :return: (samples, time_limit, memory_limit)
        samples: 列表，每个元素为 (input_str, output_str)
        time_limit: 时间限制字符串
        memory_limit: 内存限制字符串
    '''

    url = f'https://codeforces.com/problemset/problem/{contest_id}/{problem_index}'

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"请求失败：{e}")
    
    soup = BeautifulSoup(resp.text, 'html.parser')

    sample_inputs = []
    for inp in soup.find_all('div', class_='input'):
        pre = inp.find('pre')
        if pre:
            sample_inputs.append(pre.get_text('\n', strip=True))

    sample_outputs = []
    for out_elem in soup.find_all('div', class_='output'):
        pre = out_elem.find('pre')
        if pre:
            sample_outputs.append(pre.get_text('\n', strip=True))

    samples = list(zip(sample_inputs, sample_outputs))

    time_limit = ''
    time_elem = soup.find('div', class_='time-limit')
    if time_elem:
        time_limit = time_elem.text.replace('time limit per test', '').strip()

    memory_limit = ""
    mem_elem = soup.find('div', class_='memory-limit')
    if mem_elem:
        memory_limit = mem_elem.text.replace('memory limit per test', '').strip()
    
    return samples, time_limit, memory_limit

def parse_time_limit(text):
    """从时间限制字符串中提取数值（秒），例如 "2 seconds" -> 2"""
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    return int(float(match.group(1))) if match else 0

def parse_memory_limit(text):
    """从内存限制字符串中提取数值（MB），例如 "256 MB" -> 256"""
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else 0

def save_problem(problem_info, base_dir=None):
    '''
    save_problem 的 Docstring
    将题目信息保存到数据库和文件系统。
    :param problem_info: 包含完整信息的字典
    :param base_dir: 样例文件存放根目录（相对于项目根）
    '''
    if base_dir is None:
        base_dir = PROJECT_ROOT / 'data' / 'problems'
    else:
        base_dir = Path(base_dir)
    problem_dir = Path(base_dir) / problem_info['oj'] / problem_info['pid']
    problem_dir.mkdir(parents=True, exist_ok=True)

    time_limit_sec = parse_time_limit(problem_info.get('time_limit', ''))
    memory_limit_mb = parse_memory_limit(problem_info.get('memory_limit', ''))

    problem_id = add_problem(
        oj = problem_info['oj'],
        pid = problem_info['pid'],
        title = problem_info['title'],
        difficulty = problem_info.get('rating', 0),
        tags = ','.join(problem_info.get('tags', [])),
        sample_dir = str(problem_dir),  # 样例目录
        time_limit=time_limit_sec,
        memory_limit=memory_limit_mb
    )

    for i, (inp, out) in enumerate(problem_info.get('samples', []), start=1):
        with open(problem_dir / f"{i}.in", 'w', encoding='utf-8') as f:
            f.write(inp)

        with open(problem_dir / f"{i}.out", 'w', encoding='utf-8') as f:
            f.write(out)
        
    info_file = problem_dir / 'info.json'
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(problem_info, f, indent=2, ensure_ascii=False) #带缩进、保留中文
    return problem_id

def fetch_and_save_cf(contest_id, problem_index):
    '''
    fetch_and_save_cf 的 Docstring
    抓取并保存 Codeforces 题目的完整信息（元数据+样例）
    '''
    time.sleep(0.5)
    meta = fetch_cf_problem_meta(contest_id, problem_index)
    time.sleep(0.5)
    samples, time_limit, memory_limit = fetch_cf_samples(contest_id, problem_index)
    problem_info = {
        'oj': 'cf',
        'contest_id': contest_id,
        'problem_index': problem_index,
        'pid': f"{contest_id}{problem_index}",
        'title': meta['title'],
        'samples': samples,
        'tags': meta['tags'],
        'rating': meta['rating'],
        'time_limit': time_limit,
        'memory_limit': memory_limit,
    }

    try:
        problem_id = save_problem(problem_info)
    except Exception as e:
        raise RuntimeError(f"失败：{e}")
    return problem_id