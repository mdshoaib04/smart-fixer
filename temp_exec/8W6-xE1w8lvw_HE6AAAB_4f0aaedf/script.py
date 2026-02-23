import math

# Take two numbers as input from the user
num1 = int(input("Enter first number: "))
num2 = int(input("Enter second number: "))

# Calculate GCD using math.gcd
gcd = math.gcd(num1, num2)

print(f"The GCD of {num1} and {num2} is {gcd}")
