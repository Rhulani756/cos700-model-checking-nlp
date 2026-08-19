// infinite_loop_03.cpp
// Simulates processing a fixed batch of orders until a counter reaches the
// batch size, but the counter used in the condition is never the one that
// gets updated.
#include <iostream>

int main() {
    const int BATCH_SIZE = 15;
    int ordersProcessed = 0;
    int totalOrders = 0;

    while (ordersProcessed < BATCH_SIZE) {
        totalOrders++;          // BUG: increments the wrong variable
        std::cout << "Processed order #" << totalOrders << std::endl;
    }

    std::cout << "Batch complete. Total orders: " << totalOrders << std::endl;

    return 0;
}
