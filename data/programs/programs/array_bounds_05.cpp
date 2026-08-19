// array_bounds_05.cpp
// Looks up a fixed list of user IDs and prints the one that follows the
// currently logged in user (used for a simple "next user" feature).
#include <iostream>

int main() {
    const int NUM_USERS = 5;
    int userIds[NUM_USERS] = {101, 102, 103, 104, 105};

    int currentUserIndex = 4; // last valid index (the 5th user)
    int nextUserIndex = currentUserIndex + 1;

    std::cout << "Current user ID: " << userIds[currentUserIndex] << std::endl;
    std::cout << "Next user ID: " << userIds[nextUserIndex] << std::endl; // BUG: out of bounds read

    return 0;
}
