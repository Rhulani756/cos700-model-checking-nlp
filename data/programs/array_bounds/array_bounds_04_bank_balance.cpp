#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

// Looks up the txn recorded just before a given position
int main() {
    int txn[6];
    for (int i = 0; i < 6; i++) txn[i] = i + 100;

    // Simulates a requested position that may be the very first one
    int position = __VERIFIER_nondet_int();
    __VERIFIER_assume(position >= 0 && position <= 5);

    int previous_index = position - 1;
    printf("%s before position %d: %d\n", "txn", position, txn[previous_index]);  // previous_index is -1 when position == 0
    return 0;
}
