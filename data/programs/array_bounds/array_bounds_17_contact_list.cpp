#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

// Simple people entry tracker (novice-style demo program)
int main() {
    int entry[9];  // valid indices are 0..8
    for (int i = 0; i < 9; i++) entry[i] = i * 2;

    // Simulates an externally supplied entry position, e.g. read from
    // a menu or a request; only known to be within 0..9 inclusive.
    int pos = __VERIFIER_nondet_int();
    __VERIFIER_assume(pos >= 0 && pos <= 9);

    entry[pos] = 99;  // pos may equal 9, one past the last valid index
    printf("Updated %s at position %d\n", "entry", pos);
    return 0;
}
