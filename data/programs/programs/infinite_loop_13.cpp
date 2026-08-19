// infinite_loop_13.cpp
// A small "BankAccount" class that retries a withdrawal in a loop,
// waiting for the balance to become sufficient, but nothing in the loop
// ever changes the balance.
#include <iostream>

class BankAccount {
public:
    BankAccount(double balance) : balance(balance) {}

    void withdraw(double amount) {
        while (balance < amount) {
            std::cout << "Insufficient funds, waiting for balance to increase..." << std::endl;
            // BUG: nothing here ever increases balance, so the condition
            // never becomes false
        }
        balance -= amount;
        std::cout << "Withdrawal successful. New balance: " << balance << std::endl;
    }

private:
    double balance;
};

int main() {
    BankAccount account(50.0);
    account.withdraw(100.0); // balance is insufficient and never grows

    return 0;
}
