// division_by_zero_11.cpp
// Prints the result of dividing a fixed constant by each value in a
// countdown sequence that includes zero.
#include <iostream>

int main() {
    int constant = 360;

    for (int divisor = 3; divisor >= 0; divisor--) {
        int result = constant / divisor; // BUG: divisor reaches 0 on the last iteration
        std::cout << "360 / " << divisor << " = " << result << std::endl;
    }

    return 0;
}
