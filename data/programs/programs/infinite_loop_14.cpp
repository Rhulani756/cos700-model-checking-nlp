// infinite_loop_14.cpp
// Computes the sum of the digits of a number by repeatedly extracting
// the last digit, intending to stop once the number is reduced to 0.
#include <iostream>

int main() {
    int number = 12345;
    long long digitSum = 0;
    const long long MODULUS = 1000000007; // keeps digitSum bounded so it never overflows

    while (number != 0) {
        int lastDigit = number % 10;
        digitSum = (digitSum + lastDigit) % MODULUS;
        int reduced = number / 10;   // BUG: computed but never assigned back to 'number'
    }

    std::cout << "Digit sum: " << digitSum << std::endl;

    return 0;
}
