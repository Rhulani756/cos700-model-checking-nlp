// division_by_zero_08.cpp
// Normalizes a list of survey scores by dividing each by the range
// (max - min). If every score is identical, the range is zero.
#include <iostream>

int main() {
    const int N = 4;
    int scores[N] = {7, 7, 7, 7}; // all identical scores

    int maxScore = scores[0];
    int minScore = scores[0];
    for (int i = 1; i < N; i++) {
        if (scores[i] > maxScore) maxScore = scores[i];
        if (scores[i] < minScore) minScore = scores[i];
    }

    int range = maxScore - minScore; // BUG: this is 0 when all scores match

    for (int i = 0; i < N; i++) {
        int normalized = (scores[i] - minScore) * 100 / range;
        std::cout << "Normalized score " << i << ": " << normalized << std::endl;
    }

    return 0;
}
