// array_bounds_12.cpp
// Builds a histogram of die roll results. Each bucket index is the rolled
// value itself, but one of the test rolls is out of the expected 1-6
// range and is used as an index without validation.
#include <iostream>

int main() {
    const int NUM_BUCKETS = 6; // for die faces 1 through 6, stored at indices 0-5
    int histogram[NUM_BUCKETS] = {0, 0, 0, 0, 0, 0};

    int rolls[5] = {3, 6, 1, 7, 4}; // a 7 accidentally appears in the data

    for (int i = 0; i < 5; i++) {
        histogram[rolls[i] - 1]++;   // BUG: rolls[i] == 7 gives index 6, out of bounds
    }

    for (int i = 0; i < NUM_BUCKETS; i++) {
        std::cout << "Face " << (i + 1) << ": " << histogram[i] << std::endl;
    }

    return 0;
}
