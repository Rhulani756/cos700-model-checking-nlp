// division_by_zero_12.cpp
// Computes the average number of times each unique word appears in a
// short list of words, dividing total word count by unique word count.
#include <iostream>

int main() {
    int wordCount = 0;       // number of words actually stored (none in this run)
    int uniqueWordCount = 0; // number of distinct words found

    // Simulates an empty input: no words were added this run.

    int averageRepeats = wordCount / uniqueWordCount; // BUG: uniqueWordCount is 0

    std::cout << "Average repeats per unique word: " << averageRepeats << std::endl;

    return 0;
}
