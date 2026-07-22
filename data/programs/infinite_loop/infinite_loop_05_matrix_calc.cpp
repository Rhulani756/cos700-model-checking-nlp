#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

int main() {
    // Simulates an unpredictable starting count of rows left to process
    int remaining = __VERIFIER_nondet_int();
    __VERIFIER_assume(remaining >= -5 && remaining <= 10);

    // Intended to count down to zero, but increments instead of decrementing
    while (remaining > 0) {  // remaining is incremented below; when remaining > 0 this never terminates
        printf("Processing %s, %d left\n", "cell", remaining);
        remaining++;
    }

    printf("All %s processed\n", "rows");
    return 0;
}
