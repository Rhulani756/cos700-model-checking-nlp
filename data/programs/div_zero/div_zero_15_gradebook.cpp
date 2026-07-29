#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

int main() {
    int values[5] = {2, 4, 6, 8, 10};

    // Simulates an unpredictable filter threshold
    int threshold = __VERIFIER_nondet_int();
    __VERIFIER_assume(threshold >= 0 && threshold <= 20);

    int sum = 0;
    int matches = 0;
    for (int i = 0; i < 5; i++) {
        if (values[i] > threshold) {
            sum += values[i];
            matches++;
        }
    }

    int average = sum / matches;  // matches is 0 whenever threshold >= 10
    printf("Average of matching %s: %d\n", "assignments", average);
    return 0;
}
