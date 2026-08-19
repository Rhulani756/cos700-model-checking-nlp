// infinite_loop_11.cpp
// Walks a small linked list to count its nodes, but the loop forgets to
// advance the traversal pointer.
#include <iostream>

struct Node {
    int value;
    Node* next;
};

int main() {
    Node third{30, nullptr};
    Node second{20, &third};
    Node first{10, &second};
    Node* head = &first;

    long long count = 0;
    Node* current = head;
    while (current != nullptr) {
        count = (count + 1) % 1000000007; // kept bounded so it never overflows
        // BUG: missing "current = current->next;" so current never becomes nullptr
    }

    std::cout << "Number of nodes: " << count << std::endl;

    return 0;
}
