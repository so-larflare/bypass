import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# -------------------------------------------------
# 画一组箱线图
# -------------------------------------------------
def draw_box(ax, data, labels):
    bp = ax.boxplot(data,
                    labels=labels,
                    patch_artist=True,
                    medianprops=dict(color='black', linewidth=1),
                    showfliers=False)

    # 填色，淡蓝色
    for patch in bp['boxes']:
        patch.set_facecolor('#8db4d3')
        patch.set_alpha(0.8)

    ax.set_ylabel('处理时延/纳秒')
    ax.grid(axis='y', ls='--', alpha=0.4)
    # ax.set_xticklabels(labels, rotation=45, ha='right')

# -------------------------------------------------
# 数据
# -------------------------------------------------
def read_data(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [float(line.strip()) for line in f if line.strip()]

data1 = []
data1.append(read_data('lantency-data/way1-rx/4999-nobypass.data.txt'))
data1.append(read_data('lantency-data/way1-tx/4999-nobypass.data.txt'))
data1.append(read_data('lantency-data/way1-rx/4999-bypass.data.txt'))
data1.append(read_data('lantency-data/way1-tx/4999-bypass.data.txt'))
data1.append(read_data('lantency-data/way2/4999-bypass.data.txt'))

data2 = []
data2.append(read_data('lantency-data/way1-rx/5000-nobypass.data.txt'))
data2.append(read_data('lantency-data/way1-tx/5000-nobypass.data.txt'))
data2.append(read_data('lantency-data/way1-rx/5000-bypass.data.txt'))
data2.append(read_data('lantency-data/way1-tx/5000-bypass.data.txt'))
data2.append(read_data('lantency-data/way2/5000-bypass.data.txt'))

labels = [
    '未部署绕过方法\n接收方向',
    '未部署绕过方法\n发送方向',
    '部署第一种绕过方法\n接收方向',
    '部署第一种绕过方法\n发送方向',
    '部署第二种绕过方法'
    ]

# -------------------------------------------------
# 画左右并置子图
# -------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

draw_box(ax1, data1, labels)
ax1.set_title('背景流量')

draw_box(ax2, data2, labels)
ax2.set_title('隐蔽流量')

plt.tight_layout()
plt.show()
