// null_pointer_17.cpp
// A tiny binary search tree with a find function that returns nullptr
// when the value is absent. The caller uses the result directly.
#include <iostream>

struct TreeNode {
    int value;
    TreeNode* left;
    TreeNode* right;
};

TreeNode* find(TreeNode* node, int target) {
    if (node == nullptr || node->value == target) {
        return node;
    }
    if (target < node->value) {
        return find(node->left, target);
    }
    return find(node->right, target);
}

int main() {
    TreeNode leaf1{10, nullptr, nullptr};
    TreeNode leaf2{30, nullptr, nullptr};
    TreeNode root{20, &leaf1, &leaf2};

    TreeNode* result = find(&root, 99); // value not present in the tree

    std::cout << "Found value: " << result->value << std::endl; // BUG: result is nullptr

    return 0;
}
