#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

int main() {
    int total = 0;
    bool done;

    // Simulates an unpredictable per-iteration adjustment
    int step = __VERIFIER_nondet_int();
    __VERIFIER_assume(step >= -5 && step <= 5);

    // Meant to run until the running total goes negative
    do {
        total += step;
        done = (total < 0);  // when step >= 0, total never drops below zero
        printf("Running %s total: %d\n", "dollar", total);
    } while (!done);

    printf("Finished with total %d\n", total);
    return 0;
}
