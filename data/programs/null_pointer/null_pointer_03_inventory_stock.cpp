#include <cstdio>
#include <cstring>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

// Searches a small list of products and returns a pointer to the match,
// or nullptr if nothing matches.
const char* find_stock(const char* names[], int n, const char* target) {
    for (int i = 0; i < n; i++) {
        if (strcmp(names[i], target) == 0) {
            return names[i];
        }
    }
    return nullptr;
}

int main() {
    const char* names[3] = {"alpha", "beta", "gamma"};

    // Simulates an unpredictable requested name; choice 3 is not in the list
    int choice = __VERIFIER_nondet_int();
    __VERIFIER_assume(choice >= 0 && choice <= 3);

    const char* target = (choice == 0) ? "alpha"
                       : (choice == 1) ? "beta"
                       : (choice == 2) ? "gamma"
                       : "delta";

    const char* found = find_stock(names, 3, target);
    printf("Found %s: %s\n", "stock", found);  // found is nullptr when choice == 3
    return 0;
}
