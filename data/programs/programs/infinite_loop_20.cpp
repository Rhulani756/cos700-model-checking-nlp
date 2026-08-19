// infinite_loop_20.cpp
// A small "Countdown" class. The decrement function updates a variable
// that nothing else reads, while the loop condition checks a different,
// never-changing field.
#include <iostream>

class Countdown {
public:
    Countdown(int start) : remaining(start), unusedCopy(start) {}

    void decrement() {
        unusedCopy--;   // BUG: decrements the wrong field; 'remaining' never changes
    }

    bool isFinished() const {
        return remaining <= 0;
    }

    int getRemaining() const { return remaining; }

private:
    int remaining;
    int unusedCopy;
};

int main() {
    Countdown countdown(5);

    while (!countdown.isFinished()) {
        std::cout << countdown.getRemaining() << "..." << std::endl;
        countdown.decrement();
    }

    std::cout << "Liftoff!" << std::endl;

    return 0;
}
