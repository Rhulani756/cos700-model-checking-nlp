// division_by_zero_18.cpp
// Computes how many games each team must play against every other team
// in a round-robin tournament, dividing by (number of teams - 1).
#include <iostream>

class Tournament {
public:
    Tournament(int totalGames, int numTeams) : totalGames(totalGames), numTeams(numTeams) {}

    int gamesPerOpponent() const {
        int opponents = numTeams - 1;
        return totalGames / opponents; // BUG: opponents is 0 when numTeams == 1
    }

private:
    int totalGames;
    int numTeams;
};

int main() {
    int numTeams = 1; // only one team signed up this season

    Tournament tournament(0, numTeams);

    std::cout << "Games per opponent: " << tournament.gamesPerOpponent() << std::endl;

    return 0;
}
