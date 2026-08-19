// null_pointer_08.cpp
// Allocates a small fleet of Car objects via pointers, but the allocation
// loop condition stops one short, leaving the last pointer unset.
#include <iostream>

class Car {
public:
    Car(int id) : id(id) {}
    int getId() const { return id; }

private:
    int id;
};

int main() {
    const int FLEET_SIZE = 4;
    Car* fleet[FLEET_SIZE];

    for (int i = 0; i < FLEET_SIZE - 1; i++) {   // BUG: should be i < FLEET_SIZE
        fleet[i] = new Car(i);
    }
    fleet[FLEET_SIZE - 1] = nullptr; // last slot intentionally left empty by the bug

    for (int i = 0; i < FLEET_SIZE; i++) {
        std::cout << "Car ID: " << fleet[i]->getId() << std::endl; // BUG: fleet[3] is nullptr
    }

    return 0;
}
