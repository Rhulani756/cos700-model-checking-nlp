// null_pointer_14.cpp
// A tiny graph represented with an array of pointers to edge lists. One
// node has no edges, so its edge-list pointer is left nullptr, but the
// edge-printing routine dereferences it without checking.
#include <iostream>

struct EdgeNode {
    int destination;
    EdgeNode* next;
};

int main() {
    const int NUM_NODES = 4;
    EdgeNode* adjacency[NUM_NODES] = {nullptr, nullptr, nullptr, nullptr};

    adjacency[0] = new EdgeNode{1, nullptr};
    adjacency[1] = new EdgeNode{2, nullptr};
    // node 2 has no outgoing edges, adjacency[2] stays nullptr
    adjacency[3] = new EdgeNode{0, nullptr};

    for (int node = 0; node < NUM_NODES; node++) {
        std::cout << "Node " << node << " connects to "
                  << adjacency[node]->destination << std::endl; // BUG: adjacency[2] is nullptr
    }

    return 0;
}
