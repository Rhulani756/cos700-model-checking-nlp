// array_bounds_15.cpp
// Allocates a dynamic array sized from a "requested" count but then fills
// it using a different, larger count by mistake.
#include <iostream>

int main() {
    int requestedSize = 5;
    int actualItemsToStore = 8; // mismatch introduced by a copy-paste error

    int* values = new int[requestedSize];

    for (int i = 0; i < actualItemsToStore; i++) {   // BUG: should loop to requestedSize
        values[i] = i * i;
    }

    std::cout << "Stored " << actualItemsToStore << " squared values" << std::endl;

    delete[] values;

    return 0;
}
