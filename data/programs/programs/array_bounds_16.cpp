// array_bounds_16.cpp
// A small "Polynomial" class that stores coefficients and evaluates the
// polynomial at a given x using a loop over the degree.
#include <iostream>

class Polynomial {
public:
    Polynomial(int degree) : degree(degree) {
        coefficients = new double[degree + 1];
        for (int i = 0; i <= degree; i++) {
            coefficients[i] = 1.0; // every coefficient set to 1 for simplicity
        }
    }

    ~Polynomial() {
        delete[] coefficients;
    }

    double evaluate(double x) {
        double result = 0.0;
        double power = 1.0;
        for (int i = 0; i <= degree + 1; i++) {   // BUG: should be i <= degree
            result += coefficients[i] * power;
            power *= x;
        }
        return result;
    }

private:
    double* coefficients;
    int degree;
};

int main() {
    Polynomial p(3); // represents a cubic polynomial
    std::cout << "p(2) = " << p.evaluate(2.0) << std::endl;
    return 0;
}
