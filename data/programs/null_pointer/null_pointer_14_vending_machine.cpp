#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

struct VendingMachineNode {
    int value;
    VendingMachineNode* next;
};

int main() {
    VendingMachineNode second;
    second.value = 20;
    second.next = nullptr;  // list ends after the second stock

    VendingMachineNode first;
    first.value = 10;
    first.next = &second;

    // Simulates an unpredictable number of slots to skip forward
    int steps = __VERIFIER_nondet_int();
    __VERIFIER_assume(steps >= 1 && steps <= 3);

    VendingMachineNode* cursor = &first;
    for (int step = 0; step < steps; step++) {
        cursor = cursor->next;  // cursor may already be nullptr when steps == 3
    }

    printf("%s value after walking: %d\n", "stock", cursor->value);
    return 0;
}
