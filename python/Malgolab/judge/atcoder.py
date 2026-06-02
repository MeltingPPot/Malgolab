"""AtCoder problem crawler.

Fetches problem statements, sample test cases, and metadata from
https://atcoder.jp/ via HTML scraping (no official API available).
"""

import re
import time

import requests
from bs4 import BeautifulSoup

from .models import add_problem
from ..paths import problems_dir


HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/91.0.4472.124 Safari/537.36'
    ),
}

ATCODER_BASE = "https://atcoder.jp"


def _parse_at_pid(pid: str):
    """Parse an AtCoder problem ID like 'abc300_a'.

    Returns (contest_id: str, problem_suffix: str) or None.
    """
    match = re.match(r'^([a-z]+[0-9]+)_([a-z0-9]+)$', pid.lower())
    if match:
        return match.group(1), match.group(2)
    return None


def fetch_at_problem(contest_id: str, problem_id: str):
    """Scrape an AtCoder problem page for samples and metadata.

    Returns a dict with: title, time_limit, memory_limit, samples,
    contest_id, problem_id.
    """
    url = f"{ATCODER_BASE}/contests/{contest_id}/tasks/{problem_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"HTTP request failed: {exc}")

    soup = BeautifulSoup(resp.text, 'html.parser')

    # --- Title ---
    title = ''
    title_span = soup.find('span', class_='h2')
    if title_span:
        title = title_span.get_text(strip=True)
        # titles may look like "A - Something", strip the prefix
        if ' - ' in title:
            title = title.split(' - ', 1)[1]

    # --- Time / Memory limits ---
    time_limit = ''
    memory_limit = ''
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if 'Time Limit' in text:
            time_limit = text.replace('Time Limit:', '').strip()
        if 'Memory Limit' in text:
            memory_limit = text.replace('Memory Limit:', '').strip()

    # --- Samples ---
    samples = []
    # AtCoder uses <pre> inside sections; Japanese labels vary.
    # Search for sections containing "入力例"/"出力例" or English labels.
    parts = soup.find_all('section')
    # Another approach: find <h3> and grab next <pre>
    h3_tags = soup.find_all('h3')
    for h3 in h3_tags:
        h3_text = h3.get_text(strip=True).lower()
        if '入力例' in h3_text or 'input' in h3_text or 'sample input' in h3_text:
            pre = h3.find_next('pre')
            inp = pre.get_text('\n', strip=True) if pre else ''
            # find corresponding output
            next_h3 = pre.find_next('h3') if pre else None
            out = ''
            if next_h3:
                out_pre = next_h3.find_next('pre')
                if out_pre:
                    out = out_pre.get_text('\n', strip=True)
            samples.append((inp, out))
        elif '出力例' in h3_text or 'output' in h3_text or 'sample output' in h3_text:
            # handled together with input above
            pass

    # If no samples found via h3, try English-only layout
    if not samples:
        pre_tags = soup.find_all('pre')
        io_pairs = []
        for pre in pre_tags:
            text = pre.get_text('\n', strip=True)
            if text:
                io_pairs.append(text)
        # pair them up (input, output, input, output, ...)
        for i in range(0, len(io_pairs) - 1, 2):
            samples.append((io_pairs[i], io_pairs[i + 1]))

    return {
        'title': title,
        'time_limit': time_limit,
        'memory_limit': memory_limit,
        'samples': samples,
        'contest_id': contest_id,
        'problem_id': problem_id,
    }


def fetch_and_save_at(contest_id: str, problem_index: str):
    """Full pipeline: fetch AtCoder problem and persist to DB/disk."""
    full_pid = f"{contest_id}_{problem_index}"
    info = fetch_at_problem(contest_id, full_pid)

    time.sleep(0.5)

    prob_dir = problems_dir() / 'at' / full_pid
    prob_dir.mkdir(parents=True, exist_ok=True)

    time_sec = _parse_time(info.get('time_limit', ''))
    mem_mb = _parse_memory(info.get('memory_limit', ''))

    problem_db_id = add_problem(
        oj='at',
        pid=full_pid,
        title=info['title'],
        difficulty=0,
        tags='',
        sample_dir=str(prob_dir),
        time_limit=time_sec,
        memory_limit=mem_mb,
    )

    for i, (inp, out) in enumerate(info.get('samples', []), start=1):
        (prob_dir / f"{i}.in").write_text(inp, encoding='utf-8')
        (prob_dir / f"{i}.out").write_text(out, encoding='utf-8')

    import json
    (prob_dir / 'info.json').write_text(
        json.dumps(info, indent=2, ensure_ascii=False),
        encoding='utf-8')

    return problem_db_id


def _parse_time(text):
    """Extract seconds from AtCoder time limit, e.g. '2 sec' -> 2."""
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    return int(float(match.group(1)) * 1000) if match else 2000  # default 2s


def _parse_memory(text):
    """Extract MB from AtCoder memory limit, e.g. '1024 MB' -> 1024."""
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else 1024


def at_get_title(contest_id, problem_index):
    """Quick title-only fetch for init command."""
    full_pid = f"{contest_id}_{problem_index}"
    url = f"{ATCODER_BASE}/contests/{contest_id}/tasks/{full_pid}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        title_span = soup.find('span', class_='h2')
        if title_span:
            title = title_span.get_text(strip=True)
            if ' - ' in title:
                return title.split(' - ', 1)[1]
            return title
    except Exception:
        pass
    return ''


def at_contest_problems(contest_id):
    """Return a list of (problem_index, title) for a contest."""
    url = f"{ATCODER_BASE}/contests/{contest_id}/tasks"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to fetch contest tasks: {exc}")

    soup = BeautifulSoup(resp.text, 'html.parser')
    problems = []
    for row in soup.select('table tbody tr'):
        cols = row.find_all('td')
        if len(cols) >= 2:
            link = cols[0].find('a')
            if link:
                href = link.get('href', '')
                # href looks like /contests/abc300/tasks/abc300_a
                parts = href.rstrip('/').split('/')
                if parts:
                    problem_id = parts[-1]
                    title = cols[1].get_text(strip=True) if len(cols) > 1 else ''
                    problems.append((problem_id, title))
    return problems
