// division_by_zero_15.cpp
// A small "ParkingGarage" class that computes spaces per floor by
// dividing the total number of spaces by the number of floors.
#include <iostream>

class ParkingGarage {
public:
    ParkingGarage(int totalSpaces, int floors) : totalSpaces(totalSpaces), floors(floors) {}

    int spacesPerFloor() const {
        return totalSpaces / floors; // BUG: no check for floors == 0
    }

private:
    int totalSpaces;
    int floors;
};

int main() {
    int totalSpaces = 450;
    int floors = 0; // garage data was not initialized correctly

    ParkingGarage garage(totalSpaces, floors);

    std::cout << "Spaces per floor: " << garage.spacesPerFloor() << std::endl;

    return 0;
}
