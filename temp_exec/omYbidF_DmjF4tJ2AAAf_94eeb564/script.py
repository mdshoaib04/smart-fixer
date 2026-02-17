turn a if b == 0 else gcd(b, a % b)

x, y = map(int, input("Enter two numbers: ").split())
print("GCD of", x, "and", y, "is", gcd(x, y))