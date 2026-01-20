#include <sodium.h>
#include <stdio.h>
#include <sys/stat.h>

int main(void) {
    if (sodium_init() < 0) {
        fprintf(stderr, "libsodium init failed\n");
        return 1;
    }

    unsigned char pk[crypto_box_PUBLICKEYBYTES];
    unsigned char sk[crypto_box_SECRETKEYBYTES];

    crypto_box_keypair(pk, sk);

    FILE *f = fopen("/keys/eurydice", "wb");
    if (!f) { perror("fopen"); return 1; }
    fwrite(sk, 1, sizeof sk, f);
    fclose(f);
    chmod("/keys/eurydice", 0644);

    f = fopen("/keys/eurydice.pub", "wb");
    if (!f) { perror("fopen"); return 1; }
    fwrite(pk, 1, sizeof pk, f);
    fclose(f);
    chmod("/keys/eurydice.pub", 0644);

    return 0;
}
