### 绕过效果实验
videos目录存放绕过效果实验录屏。

### 速率实验、CPU使用率实验
iperf3-data目录存放网络传输速率实验、CPU使用率实验数据。数据来源iperf3，iperf3支持将测试日志以JSON的格式输出（传入-J参数），
测量结果记录了速率和CPU使用率，便于网络速率和CPU使用率数据的获取。
```
actual-*Mbps.json
没有部署绕过方法时，网络传输速率和CPU使用率实验结果。

way1-backgd-*Mbps.json
部署第一种绕过方法，背景流量网络传输速率和CPU使用率实验结果。

way1-covert-*Mbps.json
部署第一种绕过方法，隐蔽流量网络传输速率和CPU使用率实验结果。

way2-backgd-*Mbps.json
部署第二种绕过方法，背景流量网络传输速率和CPU使用率实验结果。

way2-covert-*Mbps.json
部署第二种绕过方法，隐蔽流量网络传输速率和CPU使用率实验结果。
```

### 数据包处理时延实验
latency-measure目录存放处理实验相关脚本和代码，lantency-data目录存放数据包处理时延数据。

测量方法是构造UDP数据包，测量单个UDP包在系统中的处理时间，以此来评估部署绕过方法对数据包处理时间的增加。

测量方法会维护一个键值对数据结构。

在数据包接收方向，主机B使用`udp_burst.py`程序向主机A发送UDP数据包，UDP的负载是数据包的编号。
如果配置发送1024个数据包，那么这1024个数据包的编号分别是0，1，2 ... 1023。
无论是否部署绕过方法，数据包先会被`__netif_receive_skb_core`函数处理。
当时，通过内核提供的`ktime_get_ns()`函数获得当前时间，以数据包负载中的编号为键，以当前时间为值，写入键值对数据结构中。
当改数据包经过`ip_local_deliver`函数时，再次获取当前时间，同键值对数据结构中的初始值进行比较，差值就是数据包在`__netif_receive_skb_core -> ip_local_deliver`之间经历的时间。

对于发送方向的数据包，当数据包被`__ip_local_out`函数处理时获得当前时间，以数据包负载中的编号为键，以当前时间为值，写入键值对数据结构中。
当改数据包经过virtio的数据包发送实现函数`start_xmit`函数时，再次获取当前时间，同键值对数据结构中的初始值进行比较，差值就是数据包在`__ip_local_out -> start_xmit`之间经历的时间。

由于内核编译环境的不同，在Ubuntu 22.04中`__netif_receive_skb_core`函数经过常量传播的优化，该函数并不能直接被插桩。
但是可以在`/proc/kallsyms`中获取其实际地址，命令如下：
```
ffffffff91b12670 t __netif_receive_skb_core.constprop.0
```

地址`ffffffff91b12670`在不同机器上会有所变化。获得实际地址后，需要手动填充到`latency-measure/01_latency_udp_rx/01_latency_udp_rx.c`文件的第110行中，形如
```
108 static struct kprobe kp1 = 
109 {
110     .addr = (kprobe_opcode_t *)0xffffffff91b12670,
111     .pre_handler = nrsc_kprobe_pre_handler,
112 };
```

实验在腾讯云S9.4XLARGE32实例中进行，该型号的云服务器使用virtio网卡。virtio网卡使用`start_xmit`函数作为网卡驱动接管带发送数据包的函数，所以实验选择针对`start_xmit`函数进行插桩。


此部分有三个子目录，分别用于测量①第一种绕过方法在接收方向对数据包处理引入的时延，
②第一种绕过方法在发送方向对数据包处理引入的时延和③第二种绕过方法对数据包处理引入的时延。
第二种绕过方法实验时并不区分数据包方向（接收或发送），因为第二种绕过方法在实现时并没有区分数据包的方向，统一处理所有方向的数据包。

在三个子目录下，各自有：
```
4999-bypass.txt：部署绕过方法，背景流量数据包处理时延
4999-nobypass.txt：不部署绕过方法，背景流量数据包处理时延
5000-bypass.txt：部署绕过方法，隐蔽流量数据包处理时延
5000-nobypass.txt：不部署绕过方法，隐蔽流量数据包处理时延
```
这四个文件均为内核日志输出文件（dmesg命令输出），筛选整理后导出到对应```.data.txt```文件。
值得一提的是，virtio出于性能考虑，没有将数据包的内容存储在skbuff的线性区域中，而是存储在分段区域中，所以`latency-measure/02_latency_udp_tx/02_latency_udp_tx.c`
中从skbuff的`skb_shared_info`结构中读取数据包的内容。
