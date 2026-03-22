import requests
import time
import json
from pathlib import Path
from bs4 import BeautifulSoup
from .models import add_problem

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
API_BASE = "https://codeforces.com/api"

def fetch_cf_problem_meta(contest_id, problem_index):
    '''
    fetch_cf_problem_meta 的 Docstring
    通过 Codeforces 官方 API 获取题目元数据（标题、标签、难度）
    使用 problemset.problems 接口，该接口返回所有题目，需要遍历查找
    :param contest_id: 比赛编号
    :param problem_index: 题目索引
    '''
    url = f"{API_BASE}/problemset.problems"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise RuntimeError(f"API返回失败：{e}")
    
    if data.get('status') != 'OK':
        raise RuntimeError(f"API返回错误：{data}")

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

def save_problem(problem_info, base_dir='data/problems'):
    '''
    save_problem 的 Docstring
    将题目信息保存到数据库和文件系统。
    :param problem_info: 包含完整信息的字典
    :param base_dir: 样例文件存放根目录（相对于项目根）
    '''
    problem_dir = Path(base_dir) / problem_info['oj'] / problem_info['pid']
    problem_dir.mkdir(parents=True, exist_ok=True)

    problem_id = add_problem(
        oj = problem_info['oj'],
        pid = problem_info['pid'],
        title = problem_info['title'],
        difficulty = problem_info.get('rating', 0),
        tags = ','.join(problem_info.get('tags', [])),
        sample_dir = str(problem_dir)  # 样例目录
    )
    print(f"题目已添加到数据库，ID: {problem_id}")

    for i, (inp, out) in enumerate(problem_info.get('samples', []), start=1):
        with open(problem_dir / f"{i}.in", 'w', encoding='utf-8') as f:
            f.write(inp)

        with open(problem_dir / f"{i}.out", 'w', encoding='utf-8') as f:
            f.write(out)
    print(f"样例已经保存到：{problem_dir}")
        
    info_file = problem_dir / 'info.json'
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(problem_info, f, indent=2, ensure_ascii=False) #带缩进、保留中文
        print(f"题目信息已保存到 {info_file}")

def fetch_and_save_cf(contest_id, problem_index):
    '''
    fetch_and_save_cf 的 Docstring
    抓取并保存 Codeforces 题目的完整信息（元数据+样例）
    '''
    print(f"正在抓取CodeForces {contest_id}{problem_index} ...")

    time.sleep(0.5)

    try:
        meta = fetch_cf_problem_meta(contest_id, problem_index)
    except Exception as e:
        print(f"API抓取失败\n: {e}")
        return
    
    time.sleep(0.5)

    try:
        samples, time_limit, memory_limit = fetch_cf_samples(contest_id, problem_index)
    except Exception as e:
        print(f"网页抓取失败: {e}")
        return
    
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
        save_problem(problem_info)
        print('成功')
    except Exception as e:
        print(f'失败：{e}')

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("用法: python -m Malgolab.judge.crawler cf <contest_id> <problem_index>")
        sys.exit(1)
    if sys.argv[1] == 'cf':
        contest_id = int(sys.argv[2])
        problem_index = sys.argv[3].upper() # 转为大写
        fetch_and_save_cf(contest_id, problem_index)
    else:
        print("目前仅支持 Codeforces (cf)")
