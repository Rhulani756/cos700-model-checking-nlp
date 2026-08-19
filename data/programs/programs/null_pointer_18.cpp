// null_pointer_18.cpp
// A minimal "Button" class that should notify a registered listener when
// clicked, but the listener pointer is never set before the first click.
#include <iostream>

class Listener {
public:
    virtual void onClick() = 0;
    virtual ~Listener() {}
};

class Button {
public:
    Button() : listener(nullptr) {}

    void setListener(Listener* l) { listener = l; }

    void click() {
        listener->onClick();   // BUG: listener may be nullptr
    }

private:
    Listener* listener;
};

int main() {
    Button button; // setListener() is never called

    button.click(); // BUG: triggers a call through a null listener pointer

    return 0;
}
