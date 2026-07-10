// array_bounds_08.cpp
// A small fixed-capacity Stack class. The push function increments the
// top index without checking whether the stack is already full.
#include <iostream>

class Stack {
public:
    Stack() : top(-1) {}

    void push(int value) {
        top++;
        data[top] = value;   // BUG: no check that top < CAPACITY
    }

    int pop() {
        int value = data[top];
        top--;
        return value;
    }

private:
    static const int CAPACITY = 5;
    int data[CAPACITY];
    int top;
};

int main() {
    Stack s;
    for (int i = 0; i < 20; i++) {   // pushes far more items than the 5-slot capacity allows
        s.push(i * 10);
    }
    std::cout << "Pushed 20 items onto a 5-slot stack" << std::endl;
    return 0;
}
