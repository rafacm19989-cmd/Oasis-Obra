#!/usr/bin/env python3
"""Mescla alterações lidas do app Oasis em data.json.

Uso: python3 sync/merge.py changes.json "17/11/2026 18:00"

changes.json = {
  "config": {...dados de config/obra...} ou null,
  "tarefas":   [{"id": "<id do doc>", "data": {...}}, ...],
  "diario":    [...], "custos": [...], "realizado": [...], "vinculos": [...]
}
Documentos com "excluido": true são removidos do espelho.
Valores em reais (custos e realizado) são convertidos em % do orçamento
antes de gravar: o espelho público não guarda valores em reais.
"""
import json, sys, os
base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(base, 'data.json')
D = json.load(open(path))
C = json.load(open(sys.argv[1]))
f = D['escala']
maxts = D.get('syncedAt', '')
if C.get('config'):
    D['config']['obra'] = C['config']
    maxts = max(maxts, C['config'].get('atualizadoEm', ''))
def limpa(col, d):
    d = dict(d)
    if col == 'custos':
        d['valor'] = round((d.get('valor') or 0) * f, 6)
        for k in ('fornecedor', 'doc', 'autor'): d.pop(k, None)
    if col == 'realizado':
        d['itens'] = {k: round((v or 0) * f, 6) for k, v in (d.get('itens') or {}).items()}
        d['total'] = round((d.get('total') or 0) * f, 6)
        d.pop('autor', None)
    return d
n = {}
for col in ('tarefas', 'diario', 'custos', 'realizado', 'vinculos'):
    D.setdefault(col, {})
    for item in C.get(col) or []:
        doc, data = item['id'], item['data']
        maxts = max(maxts, data.get('atualizadoEm', ''))
        if data.get('excluido'):
            D[col].pop(doc, None); n['removidos'] = n.get('removidos', 0) + 1
        else:
            D[col][doc] = limpa(col, data); n[col] = n.get(col, 0) + 1
D['syncedAt'] = maxts
if len(sys.argv) > 2: D['atualizadoEmTexto'] = sys.argv[2]
json.dump(D, open(path, 'w'), ensure_ascii=False, separators=(',', ':'))
print('ok', n, 'syncedAt', maxts, {c: len(D[c]) for c in ('tarefas', 'diario', 'custos', 'realizado', 'vinculos')})
