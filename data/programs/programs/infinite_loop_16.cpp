// infinite_loop_16.cpp
// Computes base raised to the power of exponent using repeated
// multiplication, counting up to the exponent.
#include <iostream>

int main() {
    int base = 2;
    int exponent = 10;
    long long result = 1;
    long long power = 0;
    const long long MODULUS = 1000000007; // keeps result bounded so it never overflows

    while (power < exponent) {
        result = (result * base) % MODULUS;
        power--;   // BUG: should be power++, this moves power away from exponent
    }

    std::cout << base << "^" << exponent << " = " << result << std::endl;

    return 0;
}
