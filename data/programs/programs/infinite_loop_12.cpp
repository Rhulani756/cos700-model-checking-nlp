// infinite_loop_12.cpp
// Checks whether a number is prime by testing divisibility from 2 up to
// the number itself.
#include <iostream>

int main() {
    int n = 97;
    bool isPrime = true;
    int divisor = 2;

    while (divisor < n) {
        if (n % divisor == 0) {
            isPrime = false;
            divisor++;
        }
        // BUG: divisor is only incremented inside the "if", so once a
        // non-divisor is tested the loop never advances again
    }

    std::cout << n << (isPrime ? " is prime" : " is not prime") << std::endl;

    return 0;
}
