def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# Example values
x, y = 56, 98
print("GCD of", x, "and", y, "is", gcd(x, y))
