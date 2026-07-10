// array_bounds_20.cpp
// Rotates a playlist array so the song at a given start position plays
// first, using direct index arithmetic instead of the modulo operator.
#include <iostream>

int main() {
    const int NUM_SONGS = 5;
    int playlist[NUM_SONGS] = {1, 2, 3, 4, 5};
    int rotated[NUM_SONGS];

    int startPosition = 3;

    for (int i = 0; i < NUM_SONGS; i++) {
        rotated[i] = playlist[startPosition + i];   // BUG: no wraparound, exceeds array on later i
    }

    std::cout << "Rotated playlist: ";
    for (int i = 0; i < NUM_SONGS; i++) {
        std::cout << rotated[i] << " ";
    }
    std::cout << std::endl;

    return 0;
}
