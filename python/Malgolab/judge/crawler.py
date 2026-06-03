import json
import re
import time
import warnings
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .models import add_problem
from ..paths import cache_dir, problems_dir, ensure_dir

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
API_BASE = "https://codeforces.com/api"
CACHE_DIR = cache_dir()
PROBLEMS_CACHE = CACHE_DIR / 'problemset.json'
CACHE_EXPIRY_DAYS = 1

def get_cached_problems():
    """Return the CF problem set from cache or API (cache TTL: 1 day)."""
    if PROBLEMS_CACHE.exists():
        mtime = PROBLEMS_CACHE.stat().st_mtime
        if time.time() - mtime < CACHE_EXPIRY_DAYS * 86400:
            try:
                return json.loads(
                    PROBLEMS_CACHE.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError) as exc:
                warnings.warn(f"Corrupted cache, re-fetching: {exc}")
                try:
                    PROBLEMS_CACHE.unlink()
                except OSError:
                    pass

    url = f"{API_BASE}/problemset.problems"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"CF API request failed: {exc}")
    if data.get('status') != 'OK':
        raise RuntimeError(f"CF API returned error: {data}")

    ensure_dir(CACHE_DIR)
    PROBLEMS_CACHE.write_text(
        json.dumps(data, indent=2), encoding='utf-8')
    return data

def fetch_cf_problem_meta(contest_id, problem_index):
    """Fetch CF problem metadata (title, tags, rating) via official API.

    Uses the problemset.problems endpoint; iterates to find the match.
    """
    data = get_cached_problems()
    for problem in data['result']['problems']:
        if (problem.get('contestId') == contest_id
                and problem.get('index') == problem_index):
            return {
                'title': problem.get('name', ''),
                'tags': problem.get('tags', []),
                'rating': problem.get('rating', 0),
            }
    raise RuntimeError(
        f"Problem not found: {contest_id}{problem_index}")

def fetch_cf_samples(contest_id, problem_index):
    """Scrape sample test cases, time limit, and memory limit from CF page.

    Returns (samples: list of (input, output), time_limit: str, memory_limit: str).
    """
    url = (f'https://codeforces.com/problemset/problem/'
           f'{contest_id}/{problem_index}')

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"HTTP request failed: {exc}")

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
        time_limit = time_elem.text.replace(
            'time limit per test', '').strip()

    memory_limit = ''
    mem_elem = soup.find('div', class_='memory-limit')
    if mem_elem:
        memory_limit = mem_elem.text.replace(
            'memory limit per test', '').strip()

    return samples, time_limit, memory_limit

def parse_time_limit(text):
    """Extract seconds from a time-limit string, e.g. '2 seconds' -> 2."""
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    return int(float(match.group(1))) if match else 0

def parse_memory_limit(text):
    """Extract MB from a memory-limit string, e.g. '256 MB' -> 256."""
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else 0

def save_problem(problem_info, base_dir=None):
    """Persist problem metadata to DB and sample files to disk.

    Returns the problem's local DB id.
    """
    if base_dir is None:
        base_dir = problems_dir()
    else:
        base_dir = Path(base_dir)

    prob_dir = Path(base_dir) / problem_info['oj'] / problem_info['pid']
    prob_dir.mkdir(parents=True, exist_ok=True)

    time_sec = parse_time_limit(problem_info.get('time_limit', ''))
    mem_mb = parse_memory_limit(problem_info.get('memory_limit', ''))

    problem_id = add_problem(
        oj=problem_info['oj'],
        pid=problem_info['pid'],
        title=problem_info['title'],
        difficulty=problem_info.get('rating', 0),
        tags=','.join(problem_info.get('tags', [])),
        sample_dir=str(prob_dir),
        time_limit=time_sec,
        memory_limit=mem_mb,
    )

    for i, (inp, out) in enumerate(
            problem_info.get('samples', []), start=1):
        (prob_dir / f"{i}.in").write_text(inp, encoding='utf-8')
        (prob_dir / f"{i}.out").write_text(out, encoding='utf-8')

    info_file = prob_dir / 'info.json'
    info_file.write_text(
        json.dumps(problem_info, indent=2, ensure_ascii=False),
        encoding='utf-8')
    return problem_id


def fetch_and_save_cf(contest_id, problem_index):
    """Full pipeline: fetch CF problem metadata + samples and persist."""
    time.sleep(0.5)
    meta = fetch_cf_problem_meta(contest_id, problem_index)
    time.sleep(0.5)
    samples, time_limit, memory_limit = fetch_cf_samples(
        contest_id, problem_index)

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
        return save_problem(problem_info)
    except Exception as exc:
        raise RuntimeError(f"Save failed: {exc}")
