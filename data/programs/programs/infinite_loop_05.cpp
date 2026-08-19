// infinite_loop_05.cpp
// A small "Timer" class that should count down from a starting number of
// seconds to zero, printing a message each second.
#include <iostream>

class Timer {
public:
    Timer(int seconds) : secondsLeft(seconds) {}

    void run() {
        while (secondsLeft > 0) {
            std::cout << secondsLeft << " seconds left" << std::endl;
            tick();
        }
        std::cout << "Time's up!" << std::endl;
    }

private:
    void tick() {
        int dummy = secondsLeft - 1; // BUG: computes the new value but never
                                      // assigns it back to secondsLeft
    }

    int secondsLeft;
};

int main() {
    Timer timer(5);
    timer.run();
    return 0;
}
