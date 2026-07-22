#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

// Reads up to 9 score values then prints a trailing summary entry
int main() {
    int score[9] = {0};

    // Simulates an unpredictable number of quizzes actually supplied
    int count = __VERIFIER_nondet_int();
    __VERIFIER_assume(count >= 0 && count <= 9);

    for (int i = 0; i < count; i++) {
        score[i] = (i + 1) * 3;
    }

    // Mistakenly treats 'count' as a valid last index instead of count-1
    printf("Last %s recorded: %d\n", "score", score[count]);  // count may equal 9, out of bounds
    return 0;
}
