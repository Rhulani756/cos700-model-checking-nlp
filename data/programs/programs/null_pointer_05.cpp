// null_pointer_05.cpp
// A small utility that duplicates a C-string, but returns nullptr when
// given an empty string. The caller does not check for that case.
#include <iostream>
#include <cstring>
#include <cstdlib>

char* duplicateIfNotEmpty(const char* input) {
    if (strlen(input) == 0) {
        return nullptr;
    }
    char* copy = new char[strlen(input) + 1];
    strcpy(copy, input);
    return copy;
}

int main() {
    const char* userInput = "";

    char* nameCopy = duplicateIfNotEmpty(userInput);

    std::cout << "Length of copied name: " << strlen(nameCopy) << std::endl; // BUG: nameCopy is nullptr

    delete[] nameCopy;

    return 0;
}
