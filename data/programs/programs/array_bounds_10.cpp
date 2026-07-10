// array_bounds_10.cpp
// Prints the last N readings from a sensor log, counting backward from
// the most recent reading.
#include <iostream>

int main() {
    const int LOG_SIZE = 10;
    int readings[LOG_SIZE] = {30, 31, 29, 28, 33, 35, 34, 32, 31, 30};

    int numToShow = 12; // mistakenly asked for more readings than exist

    std::cout << "Most recent readings: ";
    for (int i = 0; i < numToShow; i++) {
        std::cout << readings[LOG_SIZE - 1 - i] << " "; // BUG: index goes negative when i >= LOG_SIZE
    }
    std::cout << std::endl;

    return 0;
}
