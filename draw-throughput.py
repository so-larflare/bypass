import json
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

labels = ['50Mbps', '200Mbps', '1000Mbps', '8000Mbps']
labels = ['4Mbps', '10Mbps', '50Mbps', '200Mbps', '1000Mbps', '8000Mbps']

actual_cpus = []
actual_speends = []
way1backgd_cpus = []
way1backgd_speends = []
way1covert_cpus = []
way1covert_speends = []
way2backgd_cpus = []
way2backgd_speends = []
way2covert_cpus = []
way2covert_speends = []

for size in labels:
    actual_path = f"iperf3-data/actual-{size}.json"
    way1backgd_path = f"iperf3-data/way1-backgd-{size}.json"
    way1covert_path = f"iperf3-data/way1-covert-{size}.json"
    way2backgd_path = f"iperf3-data/way2-backgd-{size}.json"
    way2covert_path = f"iperf3-data/way2-covert-{size}.json"

    with open(actual_path, 'r', encoding='utf-8') as f:
        j = json.load(f)
        cpu = j['end']['cpu_utilization_percent']['host_total']
        speed = j['end']['sum_received']['bits_per_second']
        actual_cpus.append(cpu)
        actual_speends.append(speed)

    
    with open(way1backgd_path, 'r', encoding='utf-8') as f:
        j = json.load(f)
        cpu = j['end']['cpu_utilization_percent']['host_total']
        speed = j['end']['sum_received']['bits_per_second']
        way1backgd_cpus.append(cpu)
        way1backgd_speends.append(speed)

    with open(way1covert_path, 'r', encoding='utf-8') as f:
        j = json.load(f)
        cpu = j['end']['cpu_utilization_percent']['host_total']
        speed = j['end']['sum_received']['bits_per_second']
        way1covert_cpus.append(cpu)
        way1covert_speends.append(speed)

    with open(way2backgd_path, 'r', encoding='utf-8') as f:
        j = json.load(f)
        cpu = j['end']['cpu_utilization_percent']['host_total']
        speed = j['end']['sum_received']['bits_per_second']
        way2backgd_cpus.append(cpu)
        way2backgd_speends.append(speed)

    with open(way2covert_path, 'r', encoding='utf-8') as f:
        j = json.load(f)
        cpu = j['end']['cpu_utilization_percent']['host_total']
        speed = j['end']['sum_received']['bits_per_second']
        way2covert_cpus.append(cpu)
        way2covert_speends.append(speed)

# -------------------------------------------------
# 画一个子图
# -------------------------------------------------
def draw_one_group(ax, A, B, C, kinds, lables):
    # 只针对ax，不改变其他状态
    n_bars = 3
    width = 0.12
    x = np.arange(len(lables))# 组中心坐标
    offsets = (np.arange(n_bars) - (n_bars - 1) / 2) * 0.15

    ax.bar(x + offsets[0], A, width,
           label=kinds[0], color='#404D82', linewidth=0.8, edgecolor='black')
    ax.bar(x + offsets[1], B, width,
           label=kinds[1], color='#9AB4CF', linewidth=0.8, edgecolor='black')
    ax.bar(x + offsets[2], C, width,
           label=kinds[2], color='#AB5D77', linewidth=0.8, edgecolor='black')

    ax.set_xlabel('网络带宽')
    ax.set_ylabel('网络传输速率/Mbps')
    ax.set_ylim(top=8000)
    ax.set_xticks(x)
    ax.set_xticklabels(lables)

kinds = ['未部署绕过方法', '部署第一种绕过方法', '部署第二种绕过方法']

# 第一组图数据
A1 = np.array(actual_speends) / 1000000
B1 = np.array(way1backgd_speends) / 1000000
C1 = np.array(way2backgd_speends) / 1000000

# 第二组图数据
A2 = np.array(actual_speends) / 1000000
B2 = np.array(way1covert_speends) / 1000000
C2 = np.array(way2covert_speends) / 1000000

# 画左右并置子图
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
# 左图
draw_one_group(ax1, A1, B1, C1, kinds, labels)
ax1.set_title('背景流量')
# 右图
draw_one_group(ax2, A2, B2, C2, kinds, labels)
ax2.set_title('隐蔽流量')

# 总图例（放在右图下方，也可以放底部）
handles, labels = ax1.get_legend_handles_labels()
fig.legend(handles, labels, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0.02))

plt.tight_layout(rect=[0, 0.08, 1, 1])  # 给总图例留空
plt.show()

#绕过方法对背景流量网络传输速率的影响