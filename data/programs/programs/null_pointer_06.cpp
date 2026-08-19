// null_pointer_06.cpp
// A simple "Person" class where every employee has a pointer to their
// manager. The CEO has no manager (nullptr), but the reporting chain
// printer does not check for that before dereferencing.
#include <iostream>
#include <string>

class Person {
public:
    Person(std::string name, Person* manager) : name(name), manager(manager) {}

    std::string getName() const { return name; }
    Person* getManager() const { return manager; }

private:
    std::string name;
    Person* manager;
};

void printManagerName(Person* p) {
    std::cout << p->getName() << "'s manager is "
              << p->getManager()->getName() << std::endl; // BUG: manager may be nullptr
}

int main() {
    Person ceo("Diana", nullptr);
    Person employee("Sam", &ceo);

    printManagerName(&employee);
    printManagerName(&ceo); // ceo has no manager

    return 0;
}
