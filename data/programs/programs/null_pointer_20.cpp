// null_pointer_20.cpp
// A very small event queue that hands out raw pointers to Event objects.
// When the queue is empty, popFront returns nullptr, but main does not
// check the result before reading its field.
#include <iostream>
#include <string>

struct Event {
    std::string name;
};

class EventQueue {
public:
    EventQueue() : count(0) {}

    void push(const std::string& name) {
        if (count < CAPACITY) {
            events[count] = new Event{name};
            count++;
        }
    }

    Event* popFront() {
        if (count == 0) {
            return nullptr;
        }
        Event* front = events[0];
        for (int i = 1; i < count; i++) {
            events[i - 1] = events[i];
        }
        count--;
        return front;
    }

private:
    static const int CAPACITY = 10;
    Event* events[CAPACITY];
    int count;
};

int main() {
    EventQueue queue; // nothing pushed yet

    Event* next = queue.popFront(); // queue is empty, returns nullptr

    std::cout << "Next event: " << next->name << std::endl; // BUG: next is nullptr

    return 0;
}
