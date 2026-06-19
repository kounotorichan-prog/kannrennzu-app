import csv
from graphviz import Digraph

# -------------------
# 選択読み込み（安全）
# -------------------
with open('selected.txt') as f:
    selected = [s.strip() for s in f.read().split(',') if s.strip()]

# -------------------
# 疾患リスト
# -------------------
disease_list = [
    'pn', 'atelectasis', 'lung_cancer', 'copd', 'pe', 'mi', 'hf', 
    'sepsis', 'arrhythmia', 'stroke', 'gastric_cancer', 'colon_cancer', 
    'femoral_neck_fracture', 'dm', 'liver_cirrhosis', 'chronic_kidney_disease', 
    'ileus', 'prostate_cancer', 'parkinsons_disease', 'leukemia', 'schizophrenia',
    'kawasaki_disease','aso'
]

# -------------------
# 疾患ごとの深さ（ここが今回の核心🔥）
# -------------------
MAX_DEPTH_MAP = {
    'stroke': 6, 
    'sepsis': 4,
    'copd': 4,
    'pn': 7,
    'dm': 4,
    'mi': 4,
    'arrhythmia': 4,
    'pe': 3,
    'gastric_cancer': 5,
    'femoral_neck_fracture': 5,
    'atelectasis': 8,
    'lung_cancer': 6,
    'liver_cirrhosis': 8,
    'chronic_kidney_disease': 7,
    'ileus': 7,
    'prostate_cancer': 8,
    'parkinsons_disease': 8,
    'leukemia': 6,
    'schizophrenia': 6,
    'kawasaki_disease': 7,
    'aso': 7
}

# -------------------
# Graph設定（横長＋見やすさ）
# -------------------
dot = Digraph(format='svg')

dot.attr(
    rankdir='LR',
    splines='ortho',
    size="11.7,8.3!",   # A4横
    ratio="fill",
    nodesep="0.25",
    ranksep="0.35",
    margin="0.05"
)

dot.attr('node',
         fontsize='30',      # ←文字しっかり大きく
         width='2.0',
         height='1.0',
         fixedsize='false')  # ←これ重要

dot.attr('edge', fontsize='14')

dot.attr(overlap='false')

# -------------------
# ノード読み込み
# -------------------
nodes = {}
with open('nodes.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        nodes[row['node_id']] = {
         'name': row['name'],
         'category': row['category'],
         'merge_key': row.get('description', '').strip()
}

# -------------------
# エッジ読み込み
# -------------------
edges = []
with open('edges.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        edges.append((row['from_node'], row['to_node']))

# -------------------
# 疾患限定edge
# -------------------
SPECIAL_EDGES = {
    'atelectasis': [
        ('secretion_retention', 'atelectasis'),
        ('airway_obstruction', 'atelectasis'),
        ('alveolar_collapse', 'atelectasis'),
    ]
}

special_edge_set = set()

for disease, special in SPECIAL_EDGES.items():

    if disease in selected:

        special_edge_set.update(special)

# -------------------
# ★ 対象ノード（疾患ごと展開）
# -------------------
valid = set()

for disease in selected:
    depth = MAX_DEPTH_MAP.get(disease, 3)

    frontier = {disease}
    visited = {disease}

    for _ in range(depth):
        next_frontier = set()

        # 通常探索
        for f, t in edges:
            if f in frontier:

                # 他疾患に飛ばない
                if t in disease_list and t != disease:
                    continue

                if t not in visited:
                    visited.add(t)
                    next_frontier.add(t)

        if not next_frontier:
            break

        frontier = next_frontier

    
    special_frontier = {disease}

    for _ in range(depth):
        next_special = set()

        for f, t in special_edge_set:
            if t in special_frontier:
                if f not in visited:
                    visited.add(f)
                    next_special.add(f)

        if not next_special:
            break

        special_frontier = next_special


    valid |= visited

# patient追加
valid.add('patient')

def get_render_node(node_id):

    merge_key = nodes[node_id].get('merge_key')

    # mergeなし
    if not merge_key:
        return node_id

    # 同merge_keyの最初のnodeを代表にする
    for nid, data in nodes.items():
        if data.get('merge_key') == merge_key:
            return nid

    return node_id

# -------------------
# ノード描画
# -------------------
rendered = set()

for n in valid:

    render_id = get_render_node(n)

    if render_id in rendered:
        continue

    rendered.add(render_id)

    if n not in nodes:
        continue

    if n == 'patient':
        dot.node(
            render_id,
            nodes[n]['name'],
            shape='ellipse',
            style='filled',
            fillcolor="#D8BFAA",
            fontname="Tsukushi A Round Gothic Bold",
            fontsize="18"
        )

    elif n in selected:
        dot.node(
            render_id,
            nodes[n]['name'],
            shape='box',
            style='rounded,filled',
            fillcolor="#EFE3D5",
            fontname="Tsukushi A Round Gothic Bold",
            fontsize="18"
        )

    else:
        dot.node(
            render_id,
            nodes[n]['name'],
            shape='box',
            style='rounded',
            fontname="Tsukushi A Round Gothic Bold",
            fontsize="18"
        )

# -------------------
# patient → 疾患
# -------------------
for d in selected:
    if d in nodes:
        dot.edge('patient', d, color="#C2A38C", penwidth="2")

# -------------------
# patient中央
# -------------------
with dot.subgraph() as s:
    s.attr(rank='same')
    s.node('patient')

# -------------------
# エッジ描画
# -------------------
seen = set()

for f, t in edges:
    if f in valid and t in valid:
        f_render = get_render_node(f)
        t_render = get_render_node(t)
        
        edge = (f_render, t_render)

        if edge not in seen:
            dot.edge(
                f_render,
                t_render,
                arrowsize="1.5",
                penwidth="1.4",
                color="gray50"
            )
            seen.add(edge)

# -------------------
# 出力
# -------------------
dot.render('static/kannrennzu', view=False)

import os
os.environ["PATH"] += os.pathsep + "/usr/bin"

FONT = "Tsukushi A Round Gothic Bold"

dot.attr(fontname=FONT)
dot.attr('node', fontname=FONT)
dot.attr('edge', fontname=FONT)