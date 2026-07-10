// null_pointer_07.cpp
// A simple linked-list-based stack. Popping from an empty stack leaves
// "top" as nullptr, but the caller dereferences the popped node's value
// without checking.
#include <iostream>

struct Node {
    int value;
    Node* next;
};

class Stack {
public:
    Stack() : top(nullptr) {}

    void push(int value) {
        top = new Node{value, top};
    }

    Node* pop() {
        if (top == nullptr) {
            return nullptr;
        }
        Node* popped = top;
        top = top->next;
        return popped;
    }

private:
    Node* top;
};

int main() {
    Stack s;
    s.push(1);

    Node* first = s.pop();
    std::cout << "Popped: " << first->value << std::endl;

    Node* second = s.pop(); // stack is now empty, pop returns nullptr
    std::cout << "Popped: " << second->value << std::endl; // BUG: second is nullptr

    return 0;
}
