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
    'pn', 'dm', 'copd', 'pe', 'mi',
    'sepsis', 'stroke', 'arrhythmia', 'gastric_cancer', 'femoral_neck_fracture'
]

# -------------------
# 疾患ごとの深さ（ここが今回の核心🔥）
# -------------------
MAX_DEPTH_MAP = {
    'stroke': 6,      # ←長いから深く
    'sepsis': 4,
    'copd': 4,
    'pn': 4,
    'dm': 4,
    'mi': 4,
    'arrhythmia': 4,
    'pe': 3,
    'gastric_cancer': 5,
    'femoral_neck_fracture': 5
}

# -------------------
# Graph設定（横長＋見やすさ）
# -------------------
dot = Digraph(format='svg')

dot.attr(
    rankdir='LR',      # ←横方向
    splines='ortho',
    size="16,10!",     # ←横長固定
    nodesep="0.6",
    ranksep="0.5",
    margin="0.1"
)

dot.attr('node',
         fontsize='30',      # ←文字しっかり大きく
         width='2.0',
         height='1.0',
         fixedsize='false')  # ←これ重要

dot.attr('edge', fontsize='14')

# -------------------
# ノード読み込み
# -------------------
nodes = {}
with open('dev/nodes_dev.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        nodes[row['node_id']] = row['name']

# -------------------
# エッジ読み込み
# -------------------
edges = []
with open('dev/edges_dev.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        edges.append((row['from_node'], row['to_node']))

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

    valid |= visited

# patient追加
valid.add('patient')

# -------------------
# ノード描画
# -------------------
for n in valid:
    if n not in nodes:
        continue

    if n == 'patient':
        dot.node(
            n,
            nodes[n],
            shape='ellipse',
            style='filled',
            fillcolor="#D8BFAA",
            fontname="Tsukushi A Round Gothic Bold",
            fontsize="18"
        )

    elif n in selected:
        dot.node(
            n,
            nodes[n],
            shape='box',
            style='rounded,filled',
            fillcolor="#EFE3D5",
            fontname="Tsukushi A Round Gothic Bold",
            fontsize="18"
        )

    else:
        dot.node(
            n,
            nodes[n],
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
        edge = (f, t)

        if edge not in seen:
            dot.edge(
                f,
                t,
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