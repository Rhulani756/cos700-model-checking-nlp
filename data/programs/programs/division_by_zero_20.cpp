// division_by_zero_20.cpp
// A small "Election" class that computes the winning candidate's vote
// percentage by dividing their vote count by the total votes cast.
#include <iostream>

class Election {
public:
    Election(int candidateVotes, int totalVotes)
        : candidateVotes(candidateVotes), totalVotes(totalVotes) {}

    int winningPercentage() const {
        return candidateVotes * 100 / totalVotes; // BUG: no check for totalVotes == 0
    }

private:
    int candidateVotes;
    int totalVotes;
};

int main() {
    int totalVotesCast = 0; // polls just opened, no votes recorded yet

    Election election(0, totalVotesCast);

    std::cout << "Winning percentage: " << election.winningPercentage() << "%" << std::endl;

    return 0;
}
