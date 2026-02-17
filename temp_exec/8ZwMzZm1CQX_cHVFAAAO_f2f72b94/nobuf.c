#include <stdio.h>
void init_stdout(void) __attribute__((constructor));
void init_stdout(void) { setvbuf(stdout, NULL, _IONBF, 0); }
