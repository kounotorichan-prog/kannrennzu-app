from flask import Flask, render_template, request
import subprocess
import csv
import os
import time
import traceback

app = Flask(__name__)

# -------------------
# nodes_dev.csv から日本語名取得
# -------------------
name_map = {}

with open('dev/nodes_dev.csv', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        name_map[row['node_id']] = row['name']

# -------------------
# 表示する疾患
# -------------------
disease_list = [
    'pn', 'dm',
    'copd', 'pe', 'mi',
    'sepsis', 'stroke', 'arrhythmia', 'gastric_cancer', 'femoral_neck_fracture'
]

# 最大選択数
MAX_SELECTION = 3

# -------------------
# 画面
# -------------------
@app.route('/googlea4a498c42b8e6bd7.html')
def google_verify():
    return app.send_static_file('googlea4a498c42b8e6bd7.html')

@app.route('/', methods=['GET', 'POST'])
def index():

    message = None

    if request.method == 'POST':

        selected = request.form.getlist('disease')

        # -------------------
        # 0個チェック
        # -------------------
        if len(selected) == 0:

            message = "少なくとも1つは選択してください"

            return render_template(
                'index.html',
                image=None,
                ts=None,
                diseases=disease_list,
                names=name_map,
                message=message
            )

        # -------------------
        # 最大数チェック
        # -------------------
        if len(selected) > MAX_SELECTION:

            message = f"最大{MAX_SELECTION}個まで選択できます"

            return render_template(
                'index.html',
                image=None,
                ts=None,
                diseases=disease_list,
                names=name_map,
                message=message
            )

        # -------------------
        # 保存
        # -------------------
        with open('selected.txt', 'w') as f:
            f.write(','.join(selected))

        # -------------------
        # 画像削除（キャッシュ対策）
        # -------------------
        if os.path.exists('static/kannrennzu.svg'):
            os.remove('static/kannrennzu.svg')

        # -------------------
        # グラフ生成
        # -------------------
        try:

            result = subprocess.run(
                ['python3', 'make_graph_dev.py'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return result.stderr

        except Exception:
            return traceback.format_exc()

        # -------------------
        # 成功時
        # -------------------
        return render_template(
            'index.html',
            image='kannrennzu.svg',
            ts=int(time.time()),
            diseases=disease_list,
            names=name_map,
            message=None
        )

    # -------------------
    # GET（初期表示）
    # -------------------
    return render_template(
        'index.html',
        image=None,
        ts=None,
        diseases=disease_list,
        names=name_map,
        message=None
    )

# -------------------
# 起動
# -------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)