#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

int main() {
    int temp_values[3] = {40, 0, 10};  // one entry was never filled in by the user

    // Simulates an unpredictable index chosen for the calculation
    int index = __VERIFIER_nondet_int();
    __VERIFIER_assume(index >= 0 && index <= 2);

    int result = 100 / temp_values[index];  // temp_values[1] is 0
    printf("Result for %s: %d\n", "temp", result);
    return 0;
}
