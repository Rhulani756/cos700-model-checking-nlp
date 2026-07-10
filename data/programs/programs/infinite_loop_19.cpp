// infinite_loop_19.cpp
// Walks through a small 2D grid row by row, intending to stop once every
// row has been visited.
#include <iostream>

int main() {
    const int ROWS = 3;
    const int COLS = 3;
    int grid[ROWS][COLS] = {
        {1, 2, 3},
        {4, 5, 6},
        {7, 8, 9}
    };

    int row = 0;
    long long total = 0;
    const long long MODULUS = 1000000007; // keeps total bounded so it never overflows

    while (row < ROWS) {
        for (int col = 0; col < COLS; col++) {
            total = (total + grid[row][col]) % MODULUS;
        }
        row = 0;   // BUG: should be row++, this resets row back to 0 every time
    }

    std::cout << "Grid total: " << total << std::endl;

    return 0;
}
