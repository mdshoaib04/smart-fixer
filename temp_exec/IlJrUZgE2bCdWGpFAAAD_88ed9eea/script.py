def gcd(a, b):
    return a if b == 0 else gcd(b, a % b)

# Example values
x, y = 56, 98
print("GCD of", x, "and", y, "is", gcd(x, y))
