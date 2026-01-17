#!/bin/bash
# usage:  sudo ./limit.sh 80mbit

set -e

IF=eth0
RATE=${1:? "用法: sudo $0 <速率>  例: sudo $0 80mbit"}

# 1. 清理旧规则
tc qdisc del dev $IF root    2>/dev/null || true
tc qdisc del dev $IF ingress 2>/dev/null || true
tc qdisc del dev ifb0 root   2>/dev/null || true
ip link set ifb0 down        2>/dev/null || true

# 2. 准备 IFB
modprobe ifb numifbs=1
ip link set ifb0 up

# 3. 出方向限速（带 quantum 抑制警告）
tc qdisc add dev $IF root handle 1: htb default 10
tc class add dev $IF parent 1:  classid 1:1 htb rate $RATE ceil $RATE quantum 1500
tc class add dev $IF parent 1:1 classid 1:10 htb rate $RATE ceil $RATE quantum 1500

# 4. 入方向限速（IFB，同样加 quantum）
tc qdisc add dev $IF handle ffff: ingress
tc filter add dev $IF parent ffff: u32 match u32 0 0 \
        action mirred egress redirect dev ifb0
tc qdisc add dev ifb0 root handle 2: htb default 10
tc class add dev ifb0 parent 2:  classid 2:1 htb rate $RATE ceil $RATE quantum 1500
tc class add dev ifb0 parent 2:1 classid 2:10 htb rate $RATE ceil $RATE quantum 1500

echo "eth0 双向限速已设为 $RATE，无延时规则，quantum 警告已抑制。"
