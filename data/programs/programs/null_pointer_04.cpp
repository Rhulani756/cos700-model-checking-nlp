// null_pointer_04.cpp
// Builds an array of pointers to dynamically allocated Account objects.
// One loop only allocates odd-indexed accounts by mistake, then a later
// loop dereferences every slot.
#include <iostream>

class Account {
public:
    Account(double balance) : balance(balance) {}

    double getBalance() const { return balance; }

private:
    double balance;
};

int main() {
    const int NUM_ACCOUNTS = 5;
    Account* accounts[NUM_ACCOUNTS];

    for (int i = 0; i < NUM_ACCOUNTS; i++) {
        if (i % 2 == 1) {
            accounts[i] = new Account(100.0 * i);
        } else {
            accounts[i] = nullptr; // even-indexed accounts not opened yet
        }
    }

    double total = 0.0;
    for (int i = 0; i < NUM_ACCOUNTS; i++) {
        total += accounts[i]->getBalance(); // BUG: accounts[0], [2], [4] dereferenced
    }

    std::cout << "Total balance: " << total << std::endl;

    return 0;
}
