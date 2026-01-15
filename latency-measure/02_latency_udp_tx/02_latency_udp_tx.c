#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kprobes.h>
#include <linux/skbuff.h>
#include <linux/ktime.h>
#include <linux/jiffies.h>
#include <linux/tcp.h>
#include <linux/udp.h>
#include <linux/ip.h>

#define MODULE_NAME "tx_latency"
MODULE_LICENSE("GPL");
MODULE_AUTHOR("MODULE_AUTHOR");
MODULE_DESCRIPTION("MODULE_DESCRIPTION");

#define ARRIVAL_CAPACATY 16 * 1024
static u64 arrival_of[ARRIVAL_CAPACATY];

static bool is_backgd_covert_traffic(struct sk_buff *skb)
{
    u8 * data;
    u_int16_t sport, dport;
    bool a, b;
    struct iphdr * iph;
    struct udphdr * udph;

    if(!skb) return false;
    data = (u8 *)skb->data;
    if(data[0] != 0x45) return false;

    iph = (struct iphdr *)data;
    if (iph->protocol == IPPROTO_UDP)
    {
        udph = (void *)(iph + 1);
        sport = ntohs(udph->source);
        dport = ntohs(udph->dest);
        a = sport == 4999 || dport == 4999;
        b = sport == 5000 || dport == 5000;
        return !!(a || b);
    }
    return false;
}

static int ilo_kprobe_pre_handler(struct kprobe *p, struct pt_regs *regs)
{
    struct sk_buff *skb;
    struct udphdr *uh;
    
    u8 * payload;
    u32 pkt_idx;
    char * traffic_kind;

    u64 now;

    skb = (struct sk_buff *)regs->dx;

    if(!is_backgd_covert_traffic(skb)) return 0;
    uh = (struct udphdr *)((u8 *)skb->data + sizeof(struct iphdr));
    traffic_kind = ntohs(uh->dest) == 4999 ? "backgd" : "covert";
    payload = (u8 *)(uh + 1);
    memcpy(&pkt_idx, payload, 4);
    
    if(pkt_idx >= ARRIVAL_CAPACATY)
    {
        pr_info("%s: pkt_idx >= ARRIVAL_CAPACATY.", MODULE_NAME);
        return 0;
    }

    now = ktime_get_ns();
    arrival_of[pkt_idx] = now;
    //printk("%s: nrsc pkt idx %u, start time %llu.\n", MODULE_NAME, pkt_idx, now);
    return 0;
}

void callback(u8 * start, bool linear)
{
    if(!(start[12] == 0x08 && start[13] == 0x00)) return;//ipv4
    struct iphdr * iph = (struct iphdr *)((u8 *)start + sizeof(struct ethhdr));
    if(iph->protocol != IPPROTO_UDP)return;//udp
    
    struct udphdr * uh = (struct udphdr *)(iph + 1);
    u16 dport = ntohs(uh->dest);
    if(dport != 4999 && dport != 5000) return;//udp 4999 or 5000

    u8 * payload = (u8 *)(uh + 1);
    u32 pkt_idx; memcpy(&pkt_idx, payload, 4);

    if(pkt_idx >= ARRIVAL_CAPACATY)
    {
        pr_info("%s: pkt_idx >= ARRIVAL_CAPACATY.", MODULE_NAME);
        return;
    }

    u64 start_time = arrival_of[pkt_idx];
    if(start_time == 0)
    {
        pr_info("%s: start time error.\n", MODULE_NAME);
        return;
    }
    u64 current_time = ktime_get_ns();
    u64 latency = current_time - start_time;

    pr_info("%s: start_xmit %u/%s %s udp pkt idx %u starttime %llu endtime %llu latency {%llu}.\n",
        MODULE_NAME,
        dport,
        dport == 4999 ? "backgd" : "covert",
        linear ? "linear" : "non-li",
        pkt_idx,
        start_time,
        current_time,
        latency);

    arrival_of[pkt_idx] = 0;
}
static int start_xmit_kprobe_pre_handler(struct kprobe *p, struct pt_regs *regs)
{
    struct sk_buff * skb = (struct sk_buff *)regs->di;

	if (!skb_is_nonlinear(skb))// 确保是paged data
    {
		callback((void *)skb->data, true);
		return 0;
	}

	struct skb_shared_info *shinfo = skb_shinfo(skb);
	//pr_info("skb is nonlinear, nr_frags=%u, len=%u\n", shinfo->nr_frags, skb->len);

    unsigned int i;
	for (i = 0; i < shinfo->nr_frags; i++)
	{
        skb_frag_t * frag = &shinfo->frags[i];
        unsigned int len  = frag->bv_len;
        unsigned int offset = frag->bv_offset;

        void * vaddr = kmap_local_page(frag->bv_page);   /* 5.15+ 推荐接口 */
        if(false)
        {
            print_hex_dump(KERN_INFO, "frag: ", DUMP_PREFIX_OFFSET, 16, 1, vaddr + offset, len, true);
        }

        callback(vaddr + offset, false);

        kunmap_local(vaddr);
	}

    return 0;
}

static struct kprobe kp1 =
{
    .symbol_name = "__ip_local_out",
    .pre_handler = ilo_kprobe_pre_handler,
};
static struct kprobe kp2 = 
{
    .symbol_name = "start_xmit",
    .pre_handler = start_xmit_kprobe_pre_handler,
};
static int __init latency_udp_tx_init(void)
{   
    register_kprobe(&kp1);
    register_kprobe(&kp2);

    pr_info("%s: Module loaded.", MODULE_NAME);
    return 0;
}
static void __exit latency_udp_tx_exit(void)
{
    unregister_kprobe(&kp1);
    unregister_kprobe(&kp2);

    pr_info("%s: Module unloaded.", MODULE_NAME);
}

module_init(latency_udp_tx_init);
module_exit(latency_udp_tx_exit);
