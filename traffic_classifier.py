from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp, icmp
import time

class TrafficClassifier(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficClassifier, self).__init__(*args, **kwargs)
        # Statistics dictionary
        self.stats = {
            'TCP':  {'count': 0, 'bytes': 0},
            'UDP':  {'count': 0, 'bytes': 0},
            'ICMP': {'count': 0, 'bytes': 0},
            'OTHER':{'count': 0, 'bytes': 0},
        }
        self.mac_to_port = {}   # learning switch table
        self.start_time = time.time()
        self.logger.info("=== Traffic Classifier Controller Started ===")

    # ── Handshake: send table-miss flow entry ──────────────────────────────
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto  = datapath.ofproto
        parser   = datapath.ofproto_parser

        # Table-miss: send every unknown packet to controller
        match  = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        self.logger.info("Switch %s connected", datapath.id)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser  = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    # ── Main packet handler ────────────────────────────────────────────────
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg      = ev.msg
        datapath = msg.datapath
        ofproto  = datapath.ofproto
        parser   = datapath.ofproto_parser
        in_port  = msg.match['in_port']

        pkt     = packet.Packet(msg.data)
        eth_pkt = pkt.get_protocol(ethernet.ethernet)

        if eth_pkt is None:
            return

        dst = eth_pkt.dst
        src = eth_pkt.src
        dpid = datapath.id

        # ── MAC learning ──────────────────────────────────────────────────
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port
        out_port = self.mac_to_port[dpid].get(dst, ofproto.OFPP_FLOOD)

        actions = [parser.OFPActionOutput(out_port)]

        # ── Traffic Classification ────────────────────────────────────────
        ip_pkt   = pkt.get_protocol(ipv4.ipv4)
        pkt_len  = len(msg.data)

        if ip_pkt:
            tcp_pkt  = pkt.get_protocol(tcp.tcp)
            udp_pkt  = pkt.get_protocol(udp.udp)
            icmp_pkt = pkt.get_protocol(icmp.icmp)

            if tcp_pkt:
                proto = 'TCP'
                detail = f"src_port={tcp_pkt.src_port} dst_port={tcp_pkt.dst_port}"
            elif udp_pkt:
                proto = 'UDP'
                detail = f"src_port={udp_pkt.src_port} dst_port={udp_pkt.dst_port}"
            elif icmp_pkt:
                proto = 'ICMP'
                detail = f"type={icmp_pkt.type} code={icmp_pkt.code}"
            else:
                proto = 'OTHER'
                detail = f"ip_proto={ip_pkt.proto}"

            self.stats[proto]['count'] += 1
            self.stats[proto]['bytes'] += pkt_len

            self.logger.info(
                "[%-5s] %s -> %s | %s | %d bytes",
                proto, ip_pkt.src, ip_pkt.dst, detail, pkt_len
            )

            # ── Install proactive flow rule so future packets bypass controller
            if out_port != ofproto.OFPP_FLOOD:
                if proto == 'TCP':
                    match = parser.OFPMatch(in_port=in_port, eth_type=0x0800,
                                            ip_proto=6,
                                            ipv4_src=ip_pkt.src, ipv4_dst=ip_pkt.dst)
                elif proto == 'UDP':
                    match = parser.OFPMatch(in_port=in_port, eth_type=0x0800,
                                            ip_proto=17,
                                            ipv4_src=ip_pkt.src, ipv4_dst=ip_pkt.dst)
                elif proto == 'ICMP':
                    match = parser.OFPMatch(in_port=in_port, eth_type=0x0800,
                                            ip_proto=1,
                                            ipv4_src=ip_pkt.src, ipv4_dst=ip_pkt.dst)
                else:
                    match = None

                if match:
                    if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                        self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                    else:
                        self.add_flow(datapath, 1, match, actions)

            # ── Print live stats every 10 packets ────────────────────────
            total = sum(v['count'] for v in self.stats.values())
            if total % 10 == 0:
                self.print_stats()

        # ── Forward the packet ────────────────────────────────────────────
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id,
            in_port=in_port, actions=actions, data=data
        )
        datapath.send_msg(out)

    def print_stats(self):
        elapsed = time.time() - self.start_time
        total_pkts = sum(v['count'] for v in self.stats.values())
        self.logger.info("\n" + "="*55)
        self.logger.info(" TRAFFIC CLASSIFICATION REPORT  (%.1fs elapsed)", elapsed)
        self.logger.info("="*55)
        self.logger.info("%-8s  %8s  %10s  %8s", "Protocol","Packets","Bytes","Share%")
        self.logger.info("-"*55)
        for proto, data in self.stats.items():
            pct = (data['count']/total_pkts*100) if total_pkts else 0
            self.logger.info("%-8s  %8d  %10d  %7.1f%%",
                             proto, data['count'], data['bytes'], pct)
        self.logger.info("="*55)
