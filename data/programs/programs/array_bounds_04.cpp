// array_bounds_04.cpp
// Simulates a simple inventory system that stores item counts for each
// day of a two week period and prints a running total.
#include <iostream>

int main() {
    const int DAYS = 14;
    int itemsSold[DAYS] = {3, 5, 2, 8, 1, 0, 4, 6, 7, 2, 3, 5, 9, 1};
    int runningTotal[DAYS];

    runningTotal[0] = itemsSold[0];
    for (int day = 1; day < DAYS + 1; day++) {   // BUG: should be day < DAYS
        runningTotal[day] = runningTotal[day - 1] + itemsSold[day];
    }

    std::cout << "Final running total: " << runningTotal[DAYS - 1] << std::endl;

    return 0;
}
