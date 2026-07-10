// infinite_loop_15.cpp
// A tiny traffic light simulator that should cycle a fixed number of
// times before stopping, but the cycle counter is compared against a
// value it can never reach.
#include <iostream>
#include <string>

int main() {
    std::string state = "RED";
    int cyclesCompleted = 0;
    int maxCycles = 3;

    while (cyclesCompleted != maxCycles) {
        if (state == "RED") {
            state = "GREEN";
        } else if (state == "GREEN") {
            state = "YELLOW";
        } else {
            state = "RED";
            cyclesCompleted += 2;   // BUG: increments by 2, so it skips over maxCycles (3) entirely
        }
        std::cout << "Light is now " << state << std::endl;
    }

    std::cout << "Finished " << maxCycles << " cycles." << std::endl;

    return 0;
}
