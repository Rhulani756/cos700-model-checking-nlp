// array_bounds_14.cpp
// Copies a fixed greeting word, letter by letter, into a fixed-size char
// array, but the destination array is sized one byte too small for the
// trailing null terminator that strcpy-equivalent manual copying adds.
#include <iostream>
#include <cstring>

int main() {
    const char* word = "Welcome";   // 7 letters
    char buffer[7];                 // BUG: needs 8 to hold "Welcome" plus '\0'

    int i = 0;
    for (; word[i] != '\0'; i++) {
        buffer[i] = word[i];
    }
    buffer[i] = '\0';   // BUG: writes to buffer[7], one past the end

    std::cout << "Copied word: " << buffer << std::endl;

    return 0;
}
