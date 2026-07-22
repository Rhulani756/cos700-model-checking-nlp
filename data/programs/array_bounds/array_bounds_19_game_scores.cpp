#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

int find_max(int arr[], int n) {
    int best = arr[0];
    for (int i = 1; i <= n; i++) {  // should be i < n
        if (arr[i] > best) {
            best = arr[i];
        }
    }
    return best;
}

int main() {
    int score[8];
    for (int i = 0; i < 8; i++) score[i] = (8 - i) * 5;

    // Simulates how many players are actually populated this run
    int n = __VERIFIER_nondet_int();
    __VERIFIER_assume(n >= 1 && n <= 8);

    int best = find_max(score, n);
    printf("Best %s among %s: %d\n", "score", "players", best);
    return 0;
}
