// array_bounds_13.cpp
// A small fixed-capacity Queue class. dequeue() advances the front index
// without checking whether the queue has become empty.
#include <iostream>

class Queue {
public:
    Queue() : front(0), count(0) {
        data[0] = 0;
    }

    void enqueue(int value) {
        data[count] = value;
        count++;
    }

    int dequeue() {
        int value = data[front];
        front++;   // BUG: nothing stops front from exceeding the filled range
        return value;
    }

private:
    static const int CAPACITY = 5;
    int data[CAPACITY];
    int front;
    int count;
};

int main() {
    Queue q;
    q.enqueue(100);
    q.enqueue(200);

    for (int i = 0; i < 7; i++) {   // dequeues more times than the capacity allows
        std::cout << "Dequeued: " << q.dequeue() << std::endl;
    }

    return 0;
}
