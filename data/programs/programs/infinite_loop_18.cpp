// infinite_loop_18.cpp
// Simulates heating water from a starting temperature up to boiling
// point, one degree at a time.
#include <iostream>

int main() {
    double currentTemp = 20.0;
    const double BOILING_POINT = 100.0;

    while (currentTemp < BOILING_POINT) {
        double newTemp = currentTemp + 1.0;
        {
            double currentTemp = newTemp;   // BUG: declares a shadowed inner
                                             // variable instead of assigning to
                                             // the outer one, so the outer
                                             // currentTemp never changes
            std::cout << "Heating... " << currentTemp << " degrees" << std::endl;
        }
    }

    std::cout << "Water is boiling!" << std::endl;

    return 0;
}
