import json
for fname in ['problems/001_two-sum.json','problems/042_construct-binary-tree-from-preorder-and-inorder-traversal.json','problems/095_find-median-from-data-stream.json']:
    with open(fname,encoding='utf-8') as f:
        data=json.load(f)
    en=data.get('description_en','')
    has_code='```' in en
    print(f'{fname}: has_code_blocks={has_code}, len_en={len(en)}')
