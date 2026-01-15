#!/usr/bin/env python3
import socket
import argparse
import sys
import struct
import time
from tqdm import tqdm

def send_udp_burst(n, host, port, interval=0.02):
    """发送 n 个 UDP 包，payload 分别是 0 到 n-1 的字符串"""
    # 用 IPv4/UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 如想手动指定本地源端口，可在这里 bind(('', 0))
    try:
        for i in tqdm(range(n), desc="Sending UDP", unit="pkt"):
            payload = struct.pack('=I', i)   # = 本地字节序，I 无符号 32 位
            sock.sendto(payload, (host, port))
            time.sleep(interval)
        print(f"已发送 {n} 个 UDP 包到 {host}:{port}")
    except Exception as e:
        print("发送失败:", e, file=sys.stderr)
    finally:
        sock.close()

def main():
    parser = argparse.ArgumentParser(
        description="批量发送 payload 为 0…N-1 的 UDP 包")
    parser.add_argument("N", type=int,
                        help="发送包数（0 到 N-1）")
    parser.add_argument("host",
                        help="目的 IP 地址")
    parser.add_argument("port", type=int,
                        help="目的端口号")
    args = parser.parse_args()

    if args.N < 0:
        parser.error("N 必须 ≥ 0")

    send_udp_burst(args.N, args.host, args.port)

if __name__ == "__main__":
    main()
