// infinite_loop_02.cpp
// Prints every even number from 0 up to a limit.
#include <iostream>

int main() {
    const int LIMIT = 20;

    for (int i = 0; i < LIMIT; i--) {   // BUG: should be i++ to move toward LIMIT
        if (i % 2 == 0) {
            std::cout << i << " ";
        }
    }
    std::cout << std::endl;

    return 0;
}
