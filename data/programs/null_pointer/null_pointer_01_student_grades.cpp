#include <cstdio>
#include <cstdlib>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

struct StudentGradesRecord {
    int score_amount;
};

int main() {
    // Simulates an unpredictable stock check result
    int flag = __VERIFIER_nondet_int();
    __VERIFIER_assume(flag == 0 || flag == 1);
    bool in_stock = (flag == 1);

    StudentGradesRecord* rec = nullptr;
    if (in_stock) {
        rec = new StudentGradesRecord();
        rec->score_amount = 42;
    }

    // Forgot to check whether rec was actually allocated
    printf("Recorded %s amount: %d\n", "score", rec->score_amount);  // rec is nullptr when flag == 0
    return 0;
}
