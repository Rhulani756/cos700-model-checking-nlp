// division_by_zero_13.cpp
// A small "Order" class that computes the price per item by dividing
// the total cost by the quantity ordered, without validating quantity.
#include <iostream>

class Order {
public:
    Order(int totalCents, int quantity) : totalCents(totalCents), quantity(quantity) {}

    int pricePerItemCents() const {
        return totalCents / quantity; // BUG: no check for quantity == 0
    }

private:
    int totalCents;
    int quantity;
};

int main() {
    int cartTotal = 2500;
    int itemsInCart = 0; // the cart was accidentally cleared before checkout

    Order order(cartTotal, itemsInCart);

    std::cout << "Price per item: " << order.pricePerItemCents() << " cents" << std::endl;

    return 0;
}
