// infinite_loop_07.cpp
// Performs a linear search through an array, intending to stop either
// when the target is found or the end of the array is reached.
#include <iostream>

int main() {
    const int N = 6;
    int values[N] = {4, 8, 15, 16, 23, 42};
    int target = 99; // not present in the array
    int i = 0;
    bool found = false;

    while (i < N && !found) {
        if (values[i] == target) {
            found = true;
            i++;
        }
        // BUG: when values[i] != target, i is never incremented, so the
        // loop condition i < N stays true forever
    }

    std::cout << "Search complete, found = " << found << std::endl;

    return 0;
}
