/*
 * ecu_sim.c  -  CAN-Sentinel Week 1: mock ECUs for normal vehicle traffic
 *
 * Simulates several ECUs on one virtual CAN bus (vcan0), each sending
 * a fixed CAN ID at its own fixed period (this regular timing is the
 * "baseline" the ML model will learn later).
 *
 *   ID     Signal            Period
 *   0x100  Engine RPM        10 ms
 *   0x150  Brake status      20 ms   (0x00 = released/normal, 0x01 = pressed)
 *   0x200  Vehicle speed     20 ms
 *   0x300  Steering angle    50 ms
 *   0x400  Engine temp       100 ms
 *
 * Build:  gcc -O2 -Wall -o ecu_sim ecu_sim.c -lm
 * Run:    ./ecu_sim vcan0        (Ctrl+C to stop, prints total frames sent)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <time.h>
#include <math.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <linux/can.h>
#include <linux/can/raw.h>

#define NUM_MSGS 5

struct msg {
    canid_t id;
    long period_ms;
    long next_ms;       /* next send time (ms since start) */
    unsigned long sent;
};

static volatile sig_atomic_t running = 1;
static void on_signal(int s) { (void)s; running = 0; }

static long now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

int main(int argc, char **argv)
{
    const char *ifname = (argc > 1) ? argv[1] : "vcan0";

    signal(SIGINT, on_signal);
    signal(SIGTERM, on_signal);

    int s = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (s < 0) { perror("socket"); return 1; }

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    if (ioctl(s, SIOCGIFINDEX, &ifr) < 0) { perror("ioctl SIOCGIFINDEX"); return 1; }

    struct sockaddr_can addr;
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;
    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0) { perror("bind"); return 1; }

    struct msg msgs[NUM_MSGS] = {
        {0x100, 10,  0, 0},
        {0x150, 20,  0, 0},
        {0x200, 20,  0, 0},
        {0x300, 50,  0, 0},
        {0x400, 100, 0, 0},
    };

    long start = now_ms();
    unsigned long total = 0;
    printf("ECU simulator running on %s (Ctrl+C to stop)\n", ifname);

    while (running) {
        long t = now_ms() - start;

        for (int i = 0; i < NUM_MSGS; i++) {
            if (t < msgs[i].next_ms) continue;

            struct can_frame f;
            memset(&f, 0, sizeof(f));
            f.can_id = msgs[i].id;

            switch (msgs[i].id) {
            case 0x100: {                      /* RPM: 800..3000, 2 bytes big-endian */
                int rpm = 1900 + (int)(1100 * sin(t / 3000.0));
                f.can_dlc = 2;
                f.data[0] = (rpm >> 8) & 0xFF;
                f.data[1] = rpm & 0xFF;
                break; }
            case 0x150:                        /* Brake status: normally released */
                f.can_dlc = 1;
                f.data[0] = 0x00;
                break;
            case 0x200: {                      /* Speed: 0..120 km/h */
                int speed = 60 + (int)(60 * sin(t / 5000.0));
                f.can_dlc = 1;
                f.data[0] = speed & 0xFF;
                break; }
            case 0x300: {                      /* Steering: -90..+90 deg, offset by 128 */
                int ang = 128 + (int)(90 * sin(t / 2000.0));
                f.can_dlc = 1;
                f.data[0] = ang & 0xFF;
                break; }
            case 0x400:                        /* Engine temperature: ~90 C */
                f.can_dlc = 1;
                f.data[0] = 90 + (rand() % 3);
                break;
            }

            if (write(s, &f, sizeof(f)) != sizeof(f)) {
                perror("write");
            } else {
                msgs[i].sent++;
                total++;
            }
            msgs[i].next_ms += msgs[i].period_ms;
        }
        usleep(500);    /* 0.5 ms tick */
    }

    printf("\n--- ECU simulator summary ---\n");
    for (int i = 0; i < NUM_MSGS; i++)
        printf("ID 0x%03X : %lu frames\n", msgs[i].id, msgs[i].sent);
    printf("TOTAL SENT: %lu\n", total);
    close(s);
    return 0;
}
