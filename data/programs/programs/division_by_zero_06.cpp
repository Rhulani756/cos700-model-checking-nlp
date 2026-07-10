// division_by_zero_06.cpp
// Computes the average gap between consecutive exam dates, dividing by
// the number of gaps (one less than the number of dates).
#include <iostream>

int main() {
    const int NUM_DATES = 1; // only one exam date this term
    int examDays[NUM_DATES] = {15};

    int totalGap = 0;
    for (int i = 1; i < NUM_DATES; i++) {
        totalGap += examDays[i] - examDays[i - 1];
    }

    int numberOfGaps = NUM_DATES - 1; // BUG: this is 0 when there's only one date
    int averageGap = totalGap / numberOfGaps;

    std::cout << "Average gap between exams: " << averageGap << std::endl;

    return 0;
}
