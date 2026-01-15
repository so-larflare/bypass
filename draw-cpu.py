import json
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

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

#print('actual_cpus', actual_cpus)
#print('actual_speends', actual_speends)
#print('way1backgd_cpus', way1backgd_cpus)
#print('way1backgd_speends', way1backgd_speends)
#print('way1covert_cpus', way1covert_cpus)
#print('way1covert_speends', way1covert_speends)
#print('way2backgd_cpus', way2backgd_cpus)
#print('way2backgd_speends', way2backgd_speends)
#print('way2covert_cpus', way2covert_cpus)
#print('way2covert_speends', way2covert_speends)

A = actual_cpus
B = way1backgd_cpus
C = way1covert_cpus
D = way2backgd_cpus
E = way2covert_cpus

data = {
    '未部署绕过方法': A,
    '第一种绕过方法（背景流量）': B,
    '第一种绕过方法（隐蔽流量）': C,
    '第二种绕过方法（背景流量）': D,
    '第二种绕过方法（隐蔽流量）': E,
}

keys = list(data.keys())
n_bars = len(keys)# 5
width  = 0.12
x = np.arange(len(labels))
offsets = (np.arange(n_bars) - (n_bars-1)/2) * 0.15
colors = ['#20254C', '#414C86', '#9DB3D2', '#ECEDEA', '#AF5A77']
fig, ax = plt.subplots(figsize=(9, 5))
for offset, key, color in zip(offsets, keys, colors):
    ax.bar(x + offset, data[key], width, label=key, color=color, linewidth=0.8, edgecolor='black')

ax.set_ylabel('CPU使用率（%）')
ax.set_xlabel('网络带宽')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.tight_layout()
plt.show()
