// array_bounds_02.cpp
// Copies an array of temperatures into a new array in reverse order.
#include <iostream>

int main() {
    const int N = 7;
    int temps[N] = {21, 23, 19, 25, 18, 22, 20};
    int reversed[N];

    for (int i = 0; i < N; i++) {
        reversed[i] = temps[N - i];   // BUG: should be temps[N - 1 - i]
    }

    std::cout << "Reversed temperatures: ";
    for (int i = 0; i < N; i++) {
        std::cout << reversed[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}
