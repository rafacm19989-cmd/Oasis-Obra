#!/usr/bin/env python3
"""Mescla alterações lidas do app Oasis em data.json.

Uso: python3 sync/merge.py changes.json "17/11/2026 18:00"

changes.json = {
  "config": {...dados de config/obra...} ou null,
  "tarefas": [{"id": "t0001", "data": {...}}, ...],
  "diario":  [{"id": "<id do doc>", "data": {...}}, ...]
}
Documentos com "excluido": true são removidos do espelho.
"""
import json, sys, os
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(base, 'data.json')
D = json.load(open(path))
C = json.load(open(sys.argv[1]))
maxts = D.get('syncedAt', '')
if C.get('config'):
    D['config']['obra'] = C['config']
    maxts = max(maxts, C['config'].get('atualizadoEm', ''))
n = {'tarefas': 0, 'diario': 0, 'removidos': 0}
for col in ('tarefas', 'diario'):
    for item in C.get(col) or []:
        doc, data = item['id'], item['data']
        maxts = max(maxts, data.get('atualizadoEm', ''))
        if data.get('excluido'):
            if D[col].pop(doc, None) is not None: n['removidos'] += 1
        else:
            D[col][doc] = data; n[col] += 1
D['syncedAt'] = maxts
if len(sys.argv) > 2: D['atualizadoEmTexto'] = sys.argv[2]
json.dump(D, open(path, 'w'), ensure_ascii=False, separators=(',', ':'))
print('ok', n, 'syncedAt', maxts, 'tarefas', len(D['tarefas']), 'diario', len(D['diario']))
