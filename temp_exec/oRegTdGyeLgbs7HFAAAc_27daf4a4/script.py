

#include<stdio.h> 
#include  // For EXIT_SUCCESS/EXIT_FAILURE

int main() {
    int numerator = 10;
    int denominator = 2; // Change this to any value, including zero for demonstration purposes
    
    if (denominator == 0) {
        printf("Error: Division by zero is not allowed.\n");
        
        // Simulating returning an error code from main. In reality, you'd exit the program here with a non-zero status.
        return -1; // Using -1 as an example