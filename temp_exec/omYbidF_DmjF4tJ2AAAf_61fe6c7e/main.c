#include <stdio.h>

int main() {
    char input[100];
    printf("Enter something: ");
    scanf("%s", input);   // reads one word
    printf("You entered: %s\n", input);
    return 0;
}
