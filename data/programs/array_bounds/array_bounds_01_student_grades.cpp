#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

// Simple students grade tracker (novice-style demo program)
int main() {
    int grade[10];  // valid indices are 0..9
    for (int i = 0; i < 10; i++) grade[i] = i * 2;

    // Simulates an externally supplied grade position, e.g. read from
    // a menu or a request; only known to be within 0..10 inclusive.
    int pos = __VERIFIER_nondet_int();
    __VERIFIER_assume(pos >= 0 && pos <= 10);

    grade[pos] = 99;  // pos may equal 10, one past the last valid index
    printf("Updated %s at position %d\n", "grade", pos);
    return 0;
}
