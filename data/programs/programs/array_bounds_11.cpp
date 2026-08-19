// array_bounds_11.cpp
// A classic bubble sort implementation for a small array of exam scores.
#include <iostream>

int main() {
    const int N = 6;
    int scores[N] = {88, 45, 67, 92, 73, 51};

    for (int pass = 0; pass < N - 1; pass++) {
        for (int i = 0; i <= N - pass; i++) {   // BUG: should be i < N - pass - 1
            if (scores[i] > scores[i + 1]) {
                int temp = scores[i];
                scores[i] = scores[i + 1];
                scores[i + 1] = temp;
            }
        }
    }

    std::cout << "Sorted scores: ";
    for (int i = 0; i < N; i++) {
        std::cout << scores[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}
