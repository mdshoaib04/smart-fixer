def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# Example
num1 = 48
num2 = 18
print("GCD is:", gcd(num1, num2))