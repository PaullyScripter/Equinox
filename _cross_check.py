# Cross-check each cog against main.py names
import ast, os, sys

# Load main names
with open('_main_names.txt') as f:
    main_names = set(line.strip() for line in f if line.strip())

# Also add builtins and standard library names to exclude
import builtins
builtin_names = set(dir(builtins))

stdlib_modules = {
    'json', 'random', 'asyncio', 're', 'math', 'io', 'os', 'datetime',
    'typing', 'collections', 'itertools', 'functools', 'uuid', 'time',
    'matplotlib', 'numpy', 'qrcode', 'aiohttp', 'httpx', 'wikipedia',
    'googletrans', 'PyDictionary',
}

# Standard library top-level names
import json, random, asyncio, re, math, io, os, datetime, uuid, time, collections, itertools, functools
stdlib_names = set()
for mod_name in ['json', 'random', 'asyncio', 're', 'math', 'io', 'os', 'uuid', 'time', 'collections', 'itertools', 'functools']:
    mod = __import__(mod_name)
    stdlib_names.update(dir(mod))

# Names defined by discord
import discord
discord_names = set(dir(discord))

# For each cog file, find undefined name references
cog_dir = 'cogs'
results = {}

for fname in sorted(os.listdir(cog_dir)):
    if not fname.endswith('.py') or fname == '__init__.py':
        continue
    path = os.path.join(cog_dir, fname)
    
    with open(path, encoding='utf-8') as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    # Names defined WITHIN this cog (at module level + class methods)
    local_names = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            local_names.add(node.name)
    
    # Find all name references in the file
    referenced = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            referenced.add(node.id)
        elif isinstance(node, ast.Attribute):
            pass  # obj.attr - we don't check attrs
    
    # Also find names from imports
    imported_names = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_names.add(alias.asname or alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imported_names.add(alias.asname or alias.name)
    
    # Names that are referenced but not locally defined and not imported
    undefined = referenced - local_names - imported_names - builtin_names - discord_names - stdlib_names - {'self', 'cls', 'True', 'False', 'None'}
    
    # Filter to only those that exist in main.py
    from_main = undefined & main_names
    
    if from_main:
        results[fname] = sorted(from_main)

# Output
total_missing = 0
for fname, names in sorted(results.items()):
    print(f'\n=== {fname} ({len(names)} missing) ===')
    for n in names:
        print(f'  {n}')
    total_missing += len(names)

print(f'\n\nTotal missing references across all cogs: {total_missing}')
