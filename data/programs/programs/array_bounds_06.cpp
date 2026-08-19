// array_bounds_06.cpp
// Sums each row of a small fixed 2D grid of quiz scores.
#include <iostream>

int main() {
    const int ROWS = 3;
    const int COLS = 4;
    int grid[ROWS][COLS] = {
        {10, 8, 9, 7},
        {6, 10, 8, 9},
        {7, 7, 8, 10}
    };

    for (int r = 0; r < ROWS; r++) {
        int rowSum = 0;
        for (int c = 0; c <= COLS; c++) {   // BUG: should be c < COLS
            rowSum += grid[r][c];
        }
        std::cout << "Row " << r << " sum: " << rowSum << std::endl;
    }

    return 0;
}
