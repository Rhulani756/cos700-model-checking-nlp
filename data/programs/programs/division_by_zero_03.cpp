// division_by_zero_03.cpp
// Prints, for a fixed total, what percentage each "share" represents as
// the number of shares decreases toward zero.
#include <iostream>

int main() {
    int total = 200;
    int shares = 5;

    while (shares >= 0) {
        int amountPerShare = total / shares; // BUG: shares reaches 0 on the last iteration
        std::cout << "With " << shares << " shares, each gets: "
                  << amountPerShare << std::endl;
        shares--;
    }

    return 0;
}
