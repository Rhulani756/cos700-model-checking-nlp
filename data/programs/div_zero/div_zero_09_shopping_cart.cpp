#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

int main() {
    // Simulates two unpredictable dollar totals from different periods
    int early_total = __VERIFIER_nondet_int();
    int late_total = __VERIFIER_nondet_int();
    __VERIFIER_assume(early_total >= -50 && early_total <= 50);
    __VERIFIER_assume(late_total >= -50 && late_total <= 50);

    int trend_gap = late_total - early_total;  // can legitimately be zero
    int average_change = (late_total - early_total) / trend_gap;  // trend_gap is 0 when late_total == early_total

    printf("Average %s change: %d\n", "dollar", average_change);
    return 0;
}
