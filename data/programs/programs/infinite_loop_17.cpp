// infinite_loop_17.cpp
// Simulates validating a sequence of pre-recorded user inputs, looping
// until a valid (positive) value is found.
#include <iostream>

int main() {
    int recordedInputs[5] = {-3, -1, -7, -2, 5};
    int position = 0;
    int validValue = -1;
    bool isValid = false;

    while (!isValid) {
        int current = recordedInputs[position];
        if (current > 0) {
            validValue = current;
            isValid = true;
        }
        // BUG: position is never incremented when current <= 0, so the
        // same negative value at index 0 is checked forever
    }

    std::cout << "First valid input: " << validValue << std::endl;

    return 0;
}
