// array_bounds_17.cpp
// Merges two sorted arrays of player rankings into one combined array by
// simply appending the second array after the first.
#include <iostream>

int main() {
    const int SIZE_A = 4;
    const int SIZE_B = 3;
    int a[SIZE_A] = {1, 3, 5, 7};
    int b[SIZE_B] = {2, 4, 6};

    int combined[SIZE_A + SIZE_B];

    for (int i = 0; i < SIZE_A; i++) {
        combined[i] = a[i];
    }

    for (int i = 0; i <= SIZE_B; i++) {   // BUG: should be i < SIZE_B
        combined[SIZE_A + i] = b[i];
    }

    std::cout << "Combined rankings: ";
    for (int i = 0; i < SIZE_A + SIZE_B; i++) {
        std::cout << combined[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}
