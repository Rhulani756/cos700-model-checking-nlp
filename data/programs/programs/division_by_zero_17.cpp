// division_by_zero_17.cpp
// Computes the width of each histogram bucket by dividing the data
// range by the number of buckets requested by the user.
#include <iostream>

int main() {
    int minValue = 0;
    int maxValue = 100;
    int numberOfBuckets = 0; // user mistakenly requested zero buckets

    int range = maxValue - minValue;
    int bucketWidth = range / numberOfBuckets; // BUG: numberOfBuckets is 0

    std::cout << "Each bucket covers a width of: " << bucketWidth << std::endl;

    return 0;
}
