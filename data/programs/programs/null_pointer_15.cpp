// null_pointer_15.cpp
// A small "BankAccount" class that supports transferring money to a
// linked savings account. The transfer method assumes a savings account
// has been linked, but the constructor leaves it unset.
#include <iostream>

class SavingsAccount {
public:
    SavingsAccount(double balance) : balance(balance) {}
    void deposit(double amount) { balance += amount; }
    double getBalance() const { return balance; }

private:
    double balance;
};

class CheckingAccount {
public:
    CheckingAccount(double balance) : balance(balance), linkedSavings(nullptr) {}

    void transferToSavings(double amount) {
        balance -= amount;
        linkedSavings->deposit(amount);   // BUG: linkedSavings was never set
    }

private:
    double balance;
    SavingsAccount* linkedSavings;
};

int main() {
    CheckingAccount checking(500.0);
    checking.transferToSavings(100.0);

    std::cout << "Transfer complete" << std::endl;

    return 0;
}
