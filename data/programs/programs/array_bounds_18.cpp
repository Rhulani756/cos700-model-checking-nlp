// array_bounds_18.cpp
// Converts a list of Celsius temperatures to Fahrenheit, storing the
// results in a second array that was declared with the wrong size.
#include <iostream>

int main() {
    const int NUM_READINGS = 9;
    double celsius[NUM_READINGS] = {0, 10, 20, 25, 30, 37, 40, 50, 100};
    double fahrenheit[NUM_READINGS - 1];   // BUG: declared one element too small

    for (int i = 0; i < NUM_READINGS; i++) {
        fahrenheit[i] = celsius[i] * 9.0 / 5.0 + 32.0;   // overflows fahrenheit on the last iteration
    }

    std::cout << "Converted " << NUM_READINGS << " temperatures" << std::endl;

    return 0;
}
