// division_by_zero_07.cpp
// A small "Trip" class that computes average speed from distance and
// elapsed time, using whole minutes and kilometers. It does not guard
// against a trip with zero elapsed time.
#include <iostream>

class Trip {
public:
    Trip(int distanceKm, int timeMinutes) : distanceKm(distanceKm), timeMinutes(timeMinutes) {}

    int averageSpeed() const {
        return distanceKm / timeMinutes; // BUG: no check for timeMinutes == 0
    }

private:
    int distanceKm;
    int timeMinutes;
};

int main() {
    int startTime = 9;
    int endTime = 9; // the trip "ended" at the same time it started

    Trip trip(120, endTime - startTime);

    std::cout << "Average speed: " << trip.averageSpeed() << " km/min" << std::endl;

    return 0;
}
