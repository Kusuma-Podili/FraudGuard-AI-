import os

EXTENSIONS = {
    '.py': 'Python',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript (React)',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript (React)',
    '.html': 'HTML',
    '.css': 'CSS',
    '.sql': 'SQL'
}

EXCLUDE_DIRS = {'.git', '.gemini', 'node_modules', '.next', 'dist', 'build', '__pycache__', 'tests', 'test', '__tests__', '.pytest_cache', 'coverage', '.system_generated'}

stats = {}
total_files = 0
total_raw_lines = 0
total_code_lines = 0

for root, dirs, files in os.walk('.'):
    # filter directories in place
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
    parts = root.replace('\\', '/').split('/')
    if any(ex in parts for ex in ['tests', 'test', '__tests__']):
        continue

    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in EXTENSIONS:
            lang = EXTENSIONS[ext]
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.readlines()
                raw_lines = len(content)
                code_lines = sum(1 for line in content if line.strip() and not line.strip().startswith(('#', '//', '/*', '*')))
                
                if lang not in stats:
                    stats[lang] = {'files': 0, 'raw': 0, 'code': 0}
                stats[lang]['files'] += 1
                stats[lang]['raw'] += raw_lines
                stats[lang]['code'] += code_lines

                total_files += 1
                total_raw_lines += raw_lines
                total_code_lines += code_lines
            except Exception:
                pass

print("=" * 68)
print("             FRAUDGUARD AI - PRODUCTION LOC METRICS")
print("=" * 68)
print(f"{'Language':<24} | {'Files':<8} | {'Code LOC':<12} | {'Raw Total LOC':<12}")
print("-" * 68)
for lang, data in sorted(stats.items(), key=lambda x: x[1]['raw'], reverse=True):
    print(f"{lang:<24} | {data['files']:>6}   | {data['code']:>10,} | {data['raw']:>12,}")
print("=" * 68)
print(f"{'TOTAL (Prod Only)':<24} | {total_files:>6}   | {total_code_lines:>10,} | {total_raw_lines:>12,}")
print("=" * 68)
