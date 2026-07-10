// division_by_zero_10.cpp
// Computes a simple "z-score-like" curve adjustment for a set of test
// scores by dividing each score's deviation from the mean by the
// average absolute deviation, without checking if that deviation is 0.
#include <iostream>

int main() {
    const int N = 4;
    int scores[N] = {80, 80, 80, 80}; // every student got the same score

    int total = 0;
    for (int i = 0; i < N; i++) {
        total += scores[i];
    }
    int mean = total / N;

    int totalDeviation = 0;
    for (int i = 0; i < N; i++) {
        int deviation = scores[i] - mean;
        if (deviation < 0) deviation = -deviation;
        totalDeviation += deviation;
    }
    int averageDeviation = totalDeviation / N; // BUG: this is 0 when all scores match the mean

    for (int i = 0; i < N; i++) {
        int adjusted = (scores[i] - mean) / averageDeviation;
        std::cout << "Adjusted score " << i << ": " << adjusted << std::endl;
    }

    return 0;
}
