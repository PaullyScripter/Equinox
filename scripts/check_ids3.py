import re
content = open('cogs/ticket_views.py', encoding='utf-8').read()
ids = re.findall('custom_id="([^"]+)"', content)
print('IDs:', ids)
print('Unique:', len(set(ids)) == len(ids))
