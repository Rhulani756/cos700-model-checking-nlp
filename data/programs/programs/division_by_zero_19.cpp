// division_by_zero_19.cpp
// Computes a scaling factor for resizing an image by dividing the target
// width by the original width.
#include <iostream>

int main() {
    int originalWidth = 0; // image metadata failed to load, defaulted to 0
    int targetWidth = 800;

    int scaleFactorPercent = targetWidth * 100 / originalWidth; // BUG: originalWidth is 0

    std::cout << "Scale factor: " << scaleFactorPercent << "%" << std::endl;

    return 0;
}
