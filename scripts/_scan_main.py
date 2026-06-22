# Extract all module-level names from main.py
import ast, sys, os

script_dir = os.path.dirname(__file__)
main_path = os.path.join(script_dir, '..', 'main.py')

with open(main_path, encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

main_names = set()
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef):
        main_names.add(node.name)
    elif isinstance(node, ast.AsyncFunctionDef):
        main_names.add(node.name)
    elif isinstance(node, ast.ClassDef):
        main_names.add(node.name)
    elif isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                main_names.add(target.id)
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            main_names.add(node.target.id)

# Also add known names from the module
extra = {
    'itertools', 'functools', 'collections', 'typing', 'discord',
    'app_commands', 'commands', 'View', 'Button', 'Modal', 'TextInput', 'Select',
}
main_names -= extra

# Save to file
with open(os.path.join(script_dir, '_main_names.txt'), 'w') as f:
    for name in sorted(main_names):
        if not name.startswith('_') or name.startswith('__'):
            f.write(name + '\n')

print(f'Found {len(main_names)} names in main.py')
print('Sample:', sorted(main_names)[:20])
