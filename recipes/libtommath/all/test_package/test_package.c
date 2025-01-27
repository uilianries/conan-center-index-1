#include <stdio.h>
#include <stdlib.h>

#include "tommath.h"

int main(void) {
    mp_int a;
    int result;

    result = mp_init(&a);
    result = mp_rand(&a, 4);
    printf("a = ");
    result = mp_fwrite(&a, 4, stdout);
    printf("\n");

    return EXIT_SUCCESS;
}
