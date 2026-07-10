// division_by_zero_01.cpp
// Computes the average of a list of numbers entered by counting only the
// ones that pass a filter condition, then dividing by that count.
#include <iostream>

int main() {
    int numbers[5] = {-2, -4, -6, -8, -10};
    int sum = 0;
    int positiveCount = 0;

    for (int i = 0; i < 5; i++) {
        if (numbers[i] > 0) {
            sum += numbers[i];
            positiveCount++;
        }
    }

    // BUG: positiveCount can be 0 if there are no positive numbers,
    // which is exactly the case for this input array
    int average = sum / positiveCount;

    std::cout << "Average of positive numbers: " << average << std::endl;

    return 0;
}
