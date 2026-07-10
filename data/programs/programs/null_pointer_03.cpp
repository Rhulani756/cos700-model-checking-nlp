// null_pointer_03.cpp
// A tiny binary search tree class. The insert function is written to
// always recurse into the root without ever creating the very first node.
#include <iostream>

struct TreeNode {
    int value;
    TreeNode* left;
    TreeNode* right;
};

class BST {
public:
    BST() : root(nullptr) {}

    void insert(int value) {
        insertHelper(root, value);
    }

    void insertHelper(TreeNode* node, int value) {
        if (value < node->value) {   // BUG: node is nullptr on first insert
            if (node->left == nullptr) {
                node->left = new TreeNode{value, nullptr, nullptr};
            } else {
                insertHelper(node->left, value);
            }
        } else {
            if (node->right == nullptr) {
                node->right = new TreeNode{value, nullptr, nullptr};
            } else {
                insertHelper(node->right, value);
            }
        }
    }

private:
    TreeNode* root;
};

int main() {
    BST tree;
    tree.insert(50);
    tree.insert(30);
    tree.insert(70);
    std::cout << "Inserted values into BST" << std::endl;
    return 0;
}
