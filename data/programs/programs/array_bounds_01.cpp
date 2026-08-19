// array_bounds_01.cpp
// A novice-style program that reads a fixed number of scores into an array
// and computes their average.
#include <iostream>

int main() {
    const int SIZE = 10;
    int scores[SIZE];

    for (int i = 0; i <= SIZE; i++) {   // BUG: should be i < SIZE
        scores[i] = i * 2;
    }

    int sum = 0;
    for (int i = 0; i < SIZE; i++) {
        sum += scores[i];
    }

    double average = static_cast<double>(sum) / SIZE;
    std::cout << "Average score: " << average << std::endl;

    return 0;
}
