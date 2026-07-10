// null_pointer_12.cpp
// A tiny fixed-size bucket array used as a very simple lookup table.
// Buckets that were never assigned a value remain nullptr, but the
// lookup function dereferences whatever it finds without checking.
#include <iostream>

struct Bucket {
    int key;
    int value;
};

int main() {
    const int NUM_BUCKETS = 5;
    Bucket* buckets[NUM_BUCKETS] = {nullptr, nullptr, nullptr, nullptr, nullptr};

    buckets[1] = new Bucket{1, 100};
    buckets[3] = new Bucket{3, 300};

    int lookupIndex = 2; // this bucket was never assigned

    std::cout << "Value at bucket 2: " << buckets[lookupIndex]->value << std::endl; // BUG: nullptr

    return 0;
}
