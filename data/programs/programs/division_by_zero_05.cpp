// division_by_zero_05.cpp
// A small "Rectangle" class that computes the aspect ratio (width divided
// by height) using whole-number units. It is constructed with a height of
// 0 by mistake in main.
#include <iostream>

class Rectangle {
public:
    Rectangle(int width, int height) : width(width), height(height) {}

    int aspectRatio() const {
        return width / height; // BUG: no guard against height == 0
    }

private:
    int width;
    int height;
};

int main() {
    int userWidth = 16;
    int userHeight = 9 - 9; // mistakenly computed as 0

    Rectangle rect(userWidth, userHeight);

    std::cout << "Aspect ratio: " << rect.aspectRatio() << std::endl;

    return 0;
}
