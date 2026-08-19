// null_pointer_01.cpp
// A minimal singly linked list with an append operation. The list keeps
// track of a tail pointer but it is never initialized for an empty list.
#include <iostream>

struct Node {
    int value;
    Node* next;
};

class LinkedList {
public:
    LinkedList() : head(nullptr), tail(nullptr) {}

    void append(int value) {
        Node* newNode = new Node{value, nullptr};
        tail->next = newNode;   // BUG: tail is nullptr when list is empty
        tail = newNode;
        if (head == nullptr) {
            head = newNode;
        }
    }

    void printAll() {
        Node* current = head;
        while (current != nullptr) {
            std::cout << current->value << " ";
            current = current->next;
        }
        std::cout << std::endl;
    }

private:
    Node* head;
    Node* tail;
};

int main() {
    LinkedList list;
    list.append(10);
    list.append(20);
    list.append(30);
    list.printAll();
    return 0;
}
