// infinite_loop_06.cpp
// Computes the factorial of a number using a loop that counts down from
// n, but the loop variable used in the condition is reset inside the
// body instead of the helper variable.
#include <iostream>

int main() {
    int n = 6;
    long long result = 1;
    int i = n;
    const long long MODULUS = 1000000007; // keeps result bounded so it never overflows

    while (i > 0) {
        result = (result * i) % MODULUS;
        i = n;   // BUG: should be i--, this resets i back to n every time
    }

    std::cout << n << "! mod " << MODULUS << " = " << result << std::endl;

    return 0;
}
