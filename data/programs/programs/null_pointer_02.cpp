// null_pointer_02.cpp
// Looks up an employee record by id in a small fixed table. If the id is
// not found, the lookup function returns nullptr, but the caller forgets
// to check for that case before using the result.
#include <iostream>
#include <cstring>

struct Employee {
    int id;
    char name[32];
};

Employee* findEmployee(Employee* employees, int count, int id) {
    for (int i = 0; i < count; i++) {
        if (employees[i].id == id) {
            return &employees[i];
        }
    }
    return nullptr;
}

int main() {
    Employee staff[3] = {
        {101, "Alice"},
        {102, "Bob"},
        {103, "Carol"}
    };

    Employee* found = findEmployee(staff, 3, 999); // id does not exist

    std::cout << "Employee name: " << found->name << std::endl; // BUG: found is nullptr

    return 0;
}
