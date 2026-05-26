import time
import re

def _natural_key_original(item):
    return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', item['name'])]

_NATURAL_KEY_REGEX = re.compile(r'(\d+)')
def _natural_key_optimized(item):
    return [int(s) if s.isdigit() else s.lower() for s in _NATURAL_KEY_REGEX.split(item['name'])]

data = [{'name': f'file_{i}_v{i%10}.txt'} for i in range(100000)]

start = time.time()
data_copy = data.copy()
data_copy.sort(key=_natural_key_original)
original_time = time.time() - start

start = time.time()
data_copy = data.copy()
data_copy.sort(key=_natural_key_optimized)
optimized_time = time.time() - start

print(f"Original: {original_time:.4f}s")
print(f"Optimized: {optimized_time:.4f}s")
print(f"Improvement: {(original_time - optimized_time) / original_time * 100:.2f}%")
