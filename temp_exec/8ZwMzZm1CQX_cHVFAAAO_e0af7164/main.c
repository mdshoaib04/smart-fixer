#include <stdio.h>

int main() {
    char name[50];
    printf("Enter your name: ");
    scanf("%s", name);   // reads a single word
    printf("Hello, %s!\n", name);
    return 0;
}
