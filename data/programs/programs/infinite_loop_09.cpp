// infinite_loop_09.cpp
// Simulates a simple menu loop that should exit once the user "chooses"
// option 0. The choice is read into a local copy that never updates the
// real loop-controlling variable.
#include <iostream>

int getNextChoice(int attempt) {
    // Simulates reading a sequence of menu choices from a user.
    int choices[5] = {2, 1, 3, 1, 0};
    return choices[attempt % 5];
}

int main() {
    int choice = 5; // any non-zero starting value
    int attempt = 0;

    while (choice != 0) {
        int currentChoice = getNextChoice(attempt);   // BUG: should assign to 'choice'
        std::cout << "You chose option: " << currentChoice << std::endl;
        attempt++;
    }

    std::cout << "Exiting menu." << std::endl;

    return 0;
}
