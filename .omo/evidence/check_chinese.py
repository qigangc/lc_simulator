import json, glob, random
files = glob.glob('problems/*.json')
sample = random.sample(files, 10)
for f in sample:
    with open(f, encoding='utf-8') as fp:
        data = json.load(fp)
    zh = data.get('description_zh','')
    en = data.get('description_en','')
    same = zh == en
    title_zh = data.get('title_zh','')
    print(f'{f}: zh==en={same}, has_zh={bool(zh)}, title_zh={title_zh}')
