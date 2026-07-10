// null_pointer_11.cpp
// A small shape factory: it creates a Circle for "circle" and a Square
// for "square", but returns nullptr for any other type string. The
// caller does not check before calling a method on the result.
#include <iostream>
#include <string>

class Shape {
public:
    virtual double area() const = 0;
    virtual ~Shape() {}
};

class Circle : public Shape {
public:
    Circle(double radius) : radius(radius) {}
    double area() const override { return 3.14159 * radius * radius; }

private:
    double radius;
};

class Square : public Shape {
public:
    Square(double side) : side(side) {}
    double area() const override { return side * side; }

private:
    double side;
};

Shape* createShape(const std::string& type) {
    if (type == "circle") {
        return new Circle(2.0);
    } else if (type == "square") {
        return new Square(3.0);
    }
    return nullptr;
}

int main() {
    Shape* shape = createShape("triangle"); // unsupported type

    std::cout << "Area: " << shape->area() << std::endl; // BUG: shape is nullptr

    return 0;
}
