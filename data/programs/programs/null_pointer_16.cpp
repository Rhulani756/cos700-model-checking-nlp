// null_pointer_16.cpp
// Searches a small inventory list for an item by name and prints its
// price. If the item is not in the inventory, the search returns
// nullptr, but the caller does not check before using the result.
#include <iostream>
#include <string>

struct Item {
    std::string name;
    double price;
};

Item* findItem(Item* inventory, int count, const std::string& name) {
    for (int i = 0; i < count; i++) {
        if (inventory[i].name == name) {
            return &inventory[i];
        }
    }
    return nullptr;
}

int main() {
    Item inventory[3] = {
        {"Hammer", 12.99},
        {"Screwdriver", 7.49},
        {"Wrench", 15.25}
    };

    Item* found = findItem(inventory, 3, "Drill"); // not in inventory

    std::cout << found->name << " costs $" << found->price << std::endl; // BUG: found is nullptr

    return 0;
}
