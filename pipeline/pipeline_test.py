import asyncio
import json
import logging
import tempfile
from pathlib import Path

from pipeline.main import run_pipeline

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")

ARRAY_BOUNDS_VIOLATION = """\
#include <iostream>

int main() {
    int values[5];
    int i = 5;
    values[i] = 5;
    return 0;
}
"""

DIVISION_BY_ZERO_VIOLATION = """\
#include <iostream>

int divide(int a, int b) {
    return a / b;
}

int main() {
    int result = divide(10, 0);
    std::cout << result << std::endl;
    return 0;
}
"""

# --- multi file/ one program ---

VEHICLE_H = """\
#ifndef VEHICLE_H
#define VEHICLE_H

class Vehicle {
public:
    Vehicle(int capacity);
    int getPassenger(int index);

private:
    int capacity;
};

#endif
"""

VEHICLE_CPP = """\
#include "vehicle.h"

Vehicle::Vehicle(int capacity) : capacity(capacity) {}

int Vehicle::getPassenger(int index) {
    int passengers[4] = {1, 2, 3, 4};
    return passengers[index];  // no bounds check — bug lives here
}
"""

MAIN_CPP = """\
#include "vehicle.h"

int main() {
    Vehicle car(4);
    int p = car.getPassenger(5);  // out of bounds, but the violation
                                   // is actually inside vehicle.cpp
    return 0;
}
"""


async def run_independent_test():
    print("\n" + "=" * 60)
    print("INDEPENDENT MODE — two unrelated exercises")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp:
        submission_dir = Path(tmp)
        (submission_dir / "array_bounds.cpp").write_text(ARRAY_BOUNDS_VIOLATION)
        (submission_dir / "div_zero.cpp").write_text(DIVISION_BY_ZERO_VIOLATION)

        result = await run_pipeline(submission_dir, mode="independent")
        print(json.dumps(result, indent=2, default=str))


async def run_combined_test():
    print("\n" + "=" * 60)
    print("COMBINED MODE — main.cpp using vehicle.cpp")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmp:
        submission_dir = Path(tmp)
        (submission_dir / "vehicle.h").write_text(VEHICLE_H)
        (submission_dir / "vehicle.cpp").write_text(VEHICLE_CPP)
        (submission_dir / "main.cpp").write_text(MAIN_CPP)

        result = await run_pipeline(submission_dir, mode="combined")
        print(json.dumps(result, indent=2, default=str))


async def main():
    await run_independent_test()
    await run_combined_test()


if __name__ == "__main__":
    asyncio.run(main())