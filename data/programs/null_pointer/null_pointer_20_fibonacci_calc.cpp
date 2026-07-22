#include <cstdio>
// Verifier-provided symbolic input / path-constraint primitives.
// The model checker treats these as opaque: __VERIFIER_nondet_int()
// returns an unconstrained symbolic integer, and __VERIFIER_assume(c)
// restricts exploration to paths where c holds. No definition is
// provided (or required) for static verification.
extern int __VERIFIER_nondet_int(void);
extern void __VERIFIER_assume(int);

class FibonacciCalcCache {
public:
    int* data;

    FibonacciCalcCache() { data = nullptr; }

    void reset() {
        delete[] data;
        data = nullptr;  // cleared after use
    }

    void load(int n) {
        data = new int[n];
        for (int i = 0; i < n; i++) data[i] = i;
    }
};

int main() {
    FibonacciCalcCache cache;
    cache.load(14);

    // Simulates whether a reset happens to be triggered before reuse
    int flag = __VERIFIER_nondet_int();
    __VERIFIER_assume(flag == 0 || flag == 1);
    if (flag == 1) {
        cache.reset();
    }

    // Code re-uses the cache assuming it is still loaded
    printf("First cached %s: %d\n", "term", cache.data[0]);  // cache.data is nullptr when flag == 1
    return 0;
}
