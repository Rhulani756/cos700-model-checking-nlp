// infinite_loop_04.cpp
// A simple number guessing simulator that "guesses" a fixed target by
// incrementing a guess value. The exit condition checks against a value
// the guess can never actually reach because of how it is updated.
#include <iostream>

int main() {
    const int TARGET = 50;
    int guess = 0;
    int step = 3;

    do {
        guess += step;
        std::cout << "Current guess: " << guess << std::endl;
    } while (guess != TARGET);   // BUG: guess increases by 3 each time and
                                  // will skip over 50 (it lands on 51), so
                                  // the loop condition is never satisfied

    std::cout << "Found the target!" << std::endl;

    return 0;
}
