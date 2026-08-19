// array_bounds_09.cpp
// A simple linear scan that compares each element to its neighbor to
// find the largest adjacent difference in a sorted array.
#include <iostream>

int main() {
    const int N = 8;
    int values[N] = {2, 4, 7, 11, 16, 22, 29, 37};

    int maxDiff = 0;
    for (int i = 0; i < N; i++) {   // BUG: should be i < N - 1
        int diff = values[i + 1] - values[i];
        if (diff > maxDiff) {
            maxDiff = diff;
        }
    }

    std::cout << "Largest adjacent difference: " << maxDiff << std::endl;

    return 0;
}
