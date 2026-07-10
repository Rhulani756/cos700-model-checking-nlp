// infinite_loop_01.cpp
// Counts down from a starting number to zero and prints each value.
#include <iostream>

int main() {
    int count = 10;

    while (count != 0) {
        std::cout << count << std::endl;
        count++;   // BUG: should be count-- to actually reach 0
    }

    std::cout << "Liftoff!" << std::endl;

    return 0;
}
