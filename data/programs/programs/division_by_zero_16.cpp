// division_by_zero_16.cpp
// A small "Vector2D" class representing integer grid displacement. The
// scaleToUnitLength function divides by the vector's length without
// checking for the zero vector.
#include <iostream>

class Vector2D {
public:
    Vector2D(int x, int y) : x(x), y(y) {}

    int approximateLength() const {
        int absX = (x < 0) ? -x : x;
        int absY = (y < 0) ? -y : y;
        return absX + absY; // simple "Manhattan length" approximation
    }

    int normalizedX() const {
        int length = approximateLength();
        return x * 100 / length; // BUG: length is 0 for the zero vector
    }

private:
    int x;
    int y;
};

int main() {
    Vector2D displacement(0, 0); // object hasn't moved, zero vector

    std::cout << "Normalized X: " << displacement.normalizedX() << std::endl;

    return 0;
}
