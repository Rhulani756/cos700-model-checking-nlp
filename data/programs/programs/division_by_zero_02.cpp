// division_by_zero_02.cpp
// A tiny calculator class with a divide operation. The class does not
// guard against a zero denominator before performing the division.
#include <iostream>

class Calculator {
public:
    int divide(int numerator, int denominator) {
        return numerator / denominator; // BUG: no check for denominator == 0
    }
};

int main() {
    Calculator calc;

    int total = 100;
    int numberOfGroups = 0; // e.g. computed elsewhere and happens to be 0

    int perGroup = calc.divide(total, numberOfGroups);

    std::cout << "Items per group: " << perGroup << std::endl;

    return 0;
}
