def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# Example usage
x = 48
y = 18
print(f"The GCD of {x} and {y} is {gcd(x, y)}")
