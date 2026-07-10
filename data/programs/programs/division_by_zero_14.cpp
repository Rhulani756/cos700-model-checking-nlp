// division_by_zero_14.cpp
// Distributes a deck of cards evenly among players, recursively halving
// the player count each round to simulate elimination, and reporting
// cards per player at each round.
#include <iostream>

void simulateRound(int totalCards, int players) {
    int cardsPerPlayer = totalCards / players; // BUG: players can reach 0, no guard
    std::cout << "Players: " << players << ", cards each: " << cardsPerPlayer << std::endl;

    int nextRoundPlayers = players / 2;
    simulateRound(totalCards, nextRoundPlayers);
}

int main() {
    simulateRound(52, 1); // players will become 0 after one halving step, then crash
    return 0;
}
