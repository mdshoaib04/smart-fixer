#include <stdio.h>

// Recursive function for GCD
int gcd(int a, int b) {
    return (b == 0) ? a : gcd(b, a % b);
}

int main() {
    int x, y;
    printf("Enter two integers: ");
    scanf("%d %d", &x, &y);

    printf("GCD of %d and %d is %d\n", x, y, gcd(x, y));
    return 0;
}
