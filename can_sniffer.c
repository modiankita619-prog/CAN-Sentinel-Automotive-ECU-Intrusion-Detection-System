/*
 * can_sniffer.c - CAN-Sentinel Week 3: Live Integration
 *
 * Reads raw CAN frames from vcan0 (real SocketCAN) and forwards each one
 * as a text line over a Unix Domain Socket to the Python detection engine,
 * for sub-millisecond, real-time inference (no file writes, no polling -
 * the Python side blocks on recv() and reacts the instant a frame arrives).
 *
 * Line format sent per frame:  <can_id_hex>,<dlc>,<byte0>,<byte1>,...,<byteN>
 * Example:                     100,8,7,208,0,0,0,0,0,0
 *
 * Build:  gcc -O2 -Wall -o can_sniffer can_sniffer.c
 * Run:    ./can_sniffer vcan0 /tmp/can_sentinel.sock
 *         (run the Python listener FIRST, in another terminal, so the
 *          socket file exists before this connects to it)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <linux/can.h>
#include <linux/can/raw.h>

static volatile sig_atomic_t running = 1;
static void on_signal(int s) { (void)s; running = 0; }

int main(int argc, char **argv)
{
    const char *ifname = (argc > 1) ? argv[1] : "vcan0";
    const char *sockpath = (argc > 2) ? argv[2] : "/tmp/can_sentinel.sock";

    signal(SIGINT, on_signal);
    signal(SIGTERM, on_signal);

    /* --- open the real CAN raw socket (same as ecu_sim.c / attacker.c) --- */
    int can_sock = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (can_sock < 0) { perror("can socket"); return 1; }

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    if (ioctl(can_sock, SIOCGIFINDEX, &ifr) < 0) { perror("ioctl"); return 1; }

    struct sockaddr_can addr;
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;
    if (bind(can_sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) { perror("bind"); return 1; }

    /* --- connect to the Python side over a Unix Domain Socket --- */
    int uds = socket(AF_UNIX, SOCK_STREAM, 0);
    if (uds < 0) { perror("uds socket"); return 1; }

    struct sockaddr_un uaddr;
    memset(&uaddr, 0, sizeof(uaddr));
    uaddr.sun_family = AF_UNIX;
    strncpy(uaddr.sun_path, sockpath, sizeof(uaddr.sun_path) - 1);

    if (connect(uds, (struct sockaddr *)&uaddr, sizeof(uaddr)) < 0) {
        perror("connect (is the Python listener running?)");
        return 1;
    }

    printf("[SNIFFER] forwarding %s frames to %s (Ctrl+C to stop)\n", ifname, sockpath);
    unsigned long forwarded = 0;

    while (running) {
        struct can_frame f;
        int n = read(can_sock, &f, sizeof(f));
        if (n != sizeof(f)) continue;

        char line[128];
        int len = snprintf(line, sizeof(line), "%X,%d", f.can_id, f.can_dlc);
        for (int i = 0; i < f.can_dlc && len < (int)sizeof(line) - 4; i++)
            len += snprintf(line + len, sizeof(line) - len, ",%d", f.data[i]);
        len += snprintf(line + len, sizeof(line) - len, "\n");

        if (write(uds, line, len) != len) {
            perror("write to python");
            break;
        }
        forwarded++;
    }

    printf("\n[SNIFFER] stopped, forwarded %lu frames\n", forwarded);
    close(uds);
    close(can_sock);
    return 0;
}
