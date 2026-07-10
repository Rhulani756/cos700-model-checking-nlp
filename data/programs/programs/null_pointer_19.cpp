// null_pointer_19.cpp
// Allocates a "jagged" 2D array (array of row pointers) where every row
// should be allocated, but a conditional accidentally skips one row.
#include <iostream>

int main() {
    const int NUM_ROWS = 4;
    int* rows[NUM_ROWS] = {nullptr, nullptr, nullptr, nullptr};

    for (int r = 0; r < NUM_ROWS; r++) {
        if (r != 2) {   // BUG: row 2 is skipped due to this unintended condition
            rows[r] = new int[3];
            for (int c = 0; c < 3; c++) {
                rows[r][c] = r * 3 + c;
            }
        }
    }

    for (int r = 0; r < NUM_ROWS; r++) {
        std::cout << "Row " << r << " first element: " << rows[r][0] << std::endl; // BUG: rows[2] is uninitialized
    }

    return 0;
}
