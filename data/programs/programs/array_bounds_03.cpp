// array_bounds_03.cpp
// A small "GradeBook" class that stores student grades and finds the
// highest grade.
#include <iostream>

class GradeBook {
public:
    GradeBook(int size) : count(size) {
        grades = new int[count];
        for (int i = 0; i < count; i++) {
            grades[i] = 50 + i;
        }
    }

    ~GradeBook() {
        delete[] grades;
    }

    int findHighest() {
        int highest = grades[0];
        for (int i = 1; i <= count; i++) {   // BUG: should be i < count
            if (grades[i] > highest) {
                highest = grades[i];
            }
        }
        return highest;
    }

private:
    int* grades;
    int count;
};

int main() {
    GradeBook book(12);
    std::cout << "Highest grade: " << book.findHighest() << std::endl;
    return 0;
}
