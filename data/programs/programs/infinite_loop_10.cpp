// infinite_loop_10.cpp
// Computes the greatest common divisor of two numbers using repeated
// subtraction, intending to stop when the two numbers become equal.
#include <iostream>

int main() {
    int a = 48;
    int b = 18;

    while (a != b) {
        if (a > b) {
            a = a - b;
        } else {
            a = b - a;   // BUG: should reassign b, not a; this can oscillate forever
        }
    }

    std::cout << "GCD: " << a << std::endl;

    return 0;
}
