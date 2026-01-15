#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kprobes.h>
#include <linux/skbuff.h>
#include <linux/ktime.h>
#include <linux/jiffies.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/ip.h>

#define MODULE_NAME "rx_latency"
MODULE_LICENSE("GPL");
MODULE_AUTHOR("MODULE_AUTHOR");
MODULE_DESCRIPTION("MODULE_DESCRIPTION");

#define ARRIVAL_CAPACATY 16 * 1024
static u64 arrival_of[ARRIVAL_CAPACATY];

static bool is_backgd_covert_traffic(struct sk_buff *skb)
{
    if(skb && ntohs(skb->protocol) == 0x0800)
    {
        u8 * data = (u8 *)skb->data;
        struct iphdr *iph = (struct iphdr *)data;

        if (iph->protocol == IPPROTO_UDP)
        {
            struct udphdr *udph = (void *)(iph + 1);
            u_int16_t sport = ntohs(udph->source);
            u_int16_t dport = ntohs(udph->dest);
            bool a = sport == 4999 || dport == 4999;
            bool b = sport == 5000 || dport == 5000;
            return !!(a || b);
        }
    }

    return false;
}

static int nrsc_kprobe_pre_handler(struct kprobe *p, struct pt_regs *regs)
{
    struct sk_buff *skb;
    struct udphdr *uh;
    u8 * payload;

    u32 pkt_idx;
    u64 now;

    skb = *(struct sk_buff **)regs->di;

    if(is_backgd_covert_traffic(skb))
    {
        uh = (struct udphdr *)((u8 *)skb->data + sizeof(struct iphdr));
        payload = (u8 *)(uh + 1);
        memcpy(&pkt_idx, payload, 4);

        if(pkt_idx >= ARRIVAL_CAPACATY) return 0;

        now = ktime_get_ns();
        arrival_of[pkt_idx] = now;

        //printk("%s: nrsc pkt idx %u, start time %llu.\n", MODULE_NAME, pkt_idx, now);
    }
    
    return 0;
}
static int ild_kprobe_pre_handler(struct kprobe *p, struct pt_regs *regs)
{
    struct sk_buff * skb = (struct sk_buff *)regs->di;

    if(!is_backgd_covert_traffic(skb))return 0;
    
    struct udphdr * uh = (struct udphdr *)((u8 *)skb->data + sizeof(struct iphdr));

    u16 dport = ntohs(uh->dest);
    u8 * payload = (u8 *)(uh + 1);
    u32 pkt_idx; memcpy(&pkt_idx, payload, 4);

    if(pkt_idx >= ARRIVAL_CAPACATY)
    {
        pr_info("%s: start time error.\n", MODULE_NAME);
        return 0;
    }

    u64 start_time = arrival_of[pkt_idx];
    if(start_time == 0)
    {
        pr_info("%s: start time error.\n", MODULE_NAME);
        return 0;
    }
    u64 current_time = ktime_get_ns();
    u64 latency = current_time - start_time;
    
    pr_info("%s: ild %u/%s udp pkt idx %u starttime %llu endtime %llu latency {%llu}.\n",
        MODULE_NAME,
        dport,
        dport == 4999 ? "backgd" : "covert",
        pkt_idx,
        start_time,
        current_time,
        latency);

    arrival_of[pkt_idx] = 0;

    return 0;
}

static struct kprobe kp1 = 
{
    .addr = (kprobe_opcode_t *)0xffffffffa4116e40,
    .pre_handler = nrsc_kprobe_pre_handler,
};
static struct kprobe kp2 =
{
    .symbol_name = "ip_local_deliver",
    .pre_handler = ild_kprobe_pre_handler,
};
static int __init latency_udp_rx_init(void)
{   
    register_kprobe(&kp1);
    register_kprobe(&kp2);

    pr_info("%s: Module loaded.", MODULE_NAME);
    return 0;
}
static void __exit latency_udp_rx_exit(void)
{
    unregister_kprobe(&kp1);
    unregister_kprobe(&kp2);

    pr_info("%s: Module unloaded.", MODULE_NAME);
}

module_init(latency_udp_rx_init);
module_exit(latency_udp_rx_exit);
