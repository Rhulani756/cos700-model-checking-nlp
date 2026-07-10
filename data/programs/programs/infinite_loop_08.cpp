// infinite_loop_08.cpp
// Runs the Collatz sequence starting from a number until it reaches 1.
#include <iostream>

int main() {
    unsigned long long n = 27;

    while (n != 1) {
        std::cout << n << " ";
        if (n % 2 == 0) {
            n = n * 2;   // BUG: should be n / 2, this makes even numbers grow instead of shrink
        } else {
            n = 3 * n + 1;
        }
    }
    std::cout << std::endl;

    std::cout << "Reached 1!" << std::endl;

    return 0;
}
