// array_bounds_19.cpp
// Recursively sums the elements of an array.
#include <iostream>

int sumArray(int arr[], int size, int index) {
    if (index > size) {   // BUG: should be index >= size (or index == size)
        return 0;
    }
    return arr[index] + sumArray(arr, size, index + 1); // reads arr[size] when index == size
}

int main() {
    const int N = 5;
    int values[N] = {4, 8, 15, 16, 23};

    int total = sumArray(values, N, 0);
    std::cout << "Total: " << total << std::endl;

    return 0;
}
