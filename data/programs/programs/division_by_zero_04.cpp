// division_by_zero_04.cpp
// Determines whether two test scores are "evenly related" by checking the
// remainder of one divided by the difference between them.
#include <iostream>

int main() {
    int scoreA = 85;
    int scoreB = 85; // same score on purpose

    int difference = scoreA - scoreB;

    // BUG: difference is 0 when the two scores are equal, causing a
    // division (modulus) by zero
    int remainder = scoreA % difference;

    std::cout << "Remainder: " << remainder << std::endl;

    return 0;
}
