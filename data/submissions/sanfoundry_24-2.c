#include <assert.h>
extern int __VERIFIER_nondet_int();

#define SIZE 5

void printEven(int i) { }
void printOdd(int i) { }

int main() {
    int array[SIZE];
    int i;
    // int num = __VERIFIER_nondet_int();
    int num = 10;

    for (i = 0; i < num; i++)
        array[i] = __VERIFIER_nondet_int();

    for (i = 0; i < num; i++)
        if (array[i] % 2 == 0)
            printEven(array[i]);

    for (i = 0; i < num; i++)
        if (array[i] % 2 != 0)
            printOdd(array[i]);

    return 0;
}