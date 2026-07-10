// null_pointer_13.cpp
// Builds a small linked list and computes its length by walking the
// "next" pointers, but the walking function assumes the list is never
// empty and reads the first node before checking if it exists.
#include <iostream>

struct Node {
    int value;
    Node* next;
};

int countNodes(Node* start) {
    std::cout << "Inspecting node with value " << start->value << std::endl; // BUG: start may be nullptr
    int count = 0;
    Node* current = start;
    while (current != nullptr) {
        count++;
        current = current->next;
    }
    return count;
}

int main() {
    Node* emptyList = nullptr; // an empty list, represented by nullptr

    int length = countNodes(emptyList);
    std::cout << "Length: " << length << std::endl;

    return 0;
}
