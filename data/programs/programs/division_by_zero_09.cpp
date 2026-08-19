// division_by_zero_09.cpp
// Distributes a total budget evenly across a number of remaining
// project phases, recursively, decrementing the phase count each time.
#include <iostream>

void distributeBudget(int totalBudget, int phasesRemaining) {
    int perPhase = totalBudget / phasesRemaining; // BUG: phasesRemaining can reach 0
    std::cout << "Phases remaining: " << phasesRemaining
              << ", budget per phase: " << perPhase << std::endl;

    if (phasesRemaining > 0) {
        distributeBudget(totalBudget, phasesRemaining - 1);
    }
}

int main() {
    distributeBudget(10000, 4); // recurses down to 0, calling the function one extra time

    return 0;
}
