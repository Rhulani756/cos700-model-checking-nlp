#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

int main() {
    int target = 25;  // odd target

    // Simulates an unpredictable starting index for the scan
    int start = __VERIFIER_nondet_int();
    __VERIFIER_assume(start >= 0 && start <= 30);

    int i;
    // Meant to stop exactly at 'target', but a step of 2 can skip over it
    for (i = start; i != target; i += 2) {  // wrong parity or overshoot means i never equals target
        printf("Checking %s index %d\n", "reading", i);
    }

    printf("Reached %s %d\n", "reading", i);
    return 0;
}
