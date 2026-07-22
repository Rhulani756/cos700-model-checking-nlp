#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

int countdown_divide(int start) {
    int value = 1000;
    int step = start;

    while (step >= 0) {
        value = value / step;  // step reaches 0 on the final iteration whenever start >= 0
        step--;
    }
    return value;
}

int main() {
    // Simulates an unpredictable starting txn count
    int start = __VERIFIER_nondet_int();
    __VERIFIER_assume(start >= -5 && start <= 10);

    int result = countdown_divide(start);
    printf("Final %s value: %d\n", "txn", result);
    return 0;
}
