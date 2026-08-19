// null_pointer_10.cpp
// A tiny doubly linked list. The removeFront function updates the new
// head's "prev" pointer without checking that a new head actually exists.
#include <iostream>

struct DNode {
    int value;
    DNode* prev;
    DNode* next;
};

class DoublyLinkedList {
public:
    DoublyLinkedList() : head(nullptr) {}

    void pushFront(int value) {
        DNode* node = new DNode{value, nullptr, head};
        if (head != nullptr) {
            head->prev = node;
        }
        head = node;
    }

    void removeFront() {
        DNode* oldHead = head;
        head = head->next;
        head->prev = nullptr;   // BUG: head may now be nullptr if list had one element
        delete oldHead;
    }

private:
    DNode* head;
};

int main() {
    DoublyLinkedList list;
    list.pushFront(42); // only one element in the list

    list.removeFront(); // removes the only element, head becomes nullptr

    std::cout << "Removed the only element from the list" << std::endl;

    return 0;
}
