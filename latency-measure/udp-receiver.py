#!/usr/bin/env python3
import socket
import struct
import sys
import argparse
import time

def recv_udp_packets(port, bind_addr='0.0.0.0'):
    """持续接收 UDP 包，解析并打印序号"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((bind_addr, port))
        print(f"Listening on UDP port {port}...", file=sys.stderr)
        while True:
            data, addr = sock.recvfrom(65536)  # 最大 UDP payload
            if len(data) == 4:
                try:
                    seq_num = struct.unpack('=I', data)[0]
                    timestamp = time.time()
                    timestamp = f"{timestamp:.6f}"
                    print(f"[{timestamp}]: {seq_num}")
                except struct.error:
                    print(f"Invalid packet from {addr}", file=sys.stderr)
            else:
                print(f"Unexpected payload size ({len(data)} bytes) from {addr}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\nStopped by user.", file=sys.stderr)
    finally:
        sock.close()

def main():
    parser = argparse.ArgumentParser(description="接收 UDP 序号包并打印序号（类似 nc -ulk）")
    parser.add_argument("port", type=int, help="监听的 UDP 端口号")
    args = parser.parse_args()

    if not (1 <= args.port <= 65535):
        parser.error("端口号必须在 1~65535 范围内")

    recv_udp_packets(args.port)

if __name__ == "__main__":
   main()
