#!/usr/bin/env python3

import re
import sys


current_file = ''
found = False

for line in sys.stdin:
    if line.startswith('=== '):
        current_file = line.strip('= \n')
        continue
    if re.search(r'[ぁ-ゖァ-ヺ]', line):
        print(f'{current_file}: {line.strip()}')
        found = True

raise SystemExit(1 if found else 0)

