// array_bounds_07.cpp
// Removes the first element of a fixed-size array by shifting every
// other element one position to the left.
#include <iostream>

int main() {
    const int SIZE = 6;
    int queue[SIZE] = {5, 10, 15, 20, 25, 30};

    for (int i = 0; i < SIZE; i++) {   // BUG: should be i < SIZE - 1
        queue[i] = queue[i + 1];
    }

    std::cout << "Queue after removing front: ";
    for (int i = 0; i < SIZE - 1; i++) {
        std::cout << queue[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}
