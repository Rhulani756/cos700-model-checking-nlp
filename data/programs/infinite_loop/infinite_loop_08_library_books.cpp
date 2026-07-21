#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

int main() {
    int sum = 0;

    // Simulates an unpredictable starting term for the running sum
    int n = __VERIFIER_nondet_int();
    __VERIFIER_assume(n >= -5 && n <= 5);

    // Meant to break once the running sum goes negative
    while (true) {
        sum += n;
        n++;
        if (sum < 0) {  // once n reaches non-negative values the sum only grows, so this is never true
            break;
        }
        printf("Running %s sum: %d\n", "titles", sum);
    }

    printf("Loop finished, sum = %d\n", sum);
    return 0;
}
