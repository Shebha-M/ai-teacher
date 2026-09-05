# Binary Tree Architecture and Operations

## Overview and Structural Invariants
A Binary Tree is a hierarchical non-linear data structure where every parent node has at most two distinct children, denoted as the Left Subtree and the Right Subtree. The top-level entry point is formally designated as the Root Node.

## AVL Balance Factor Definition
In self-balancing binary search trees (AVL Trees), the Balance Factor of any node N is defined as the height of its left subtree minus the height of its right subtree: BalanceFactor(N) = Height(Left) - Height(Right). An AVL tree strictly enforces that the Balance Factor of every node must be strictly within the set {-1, 0, +1}.

## Traversal Algorithms
Depth-First Traversal encompasses three canonical recursive strategies:
1. In-order traversal: Recursively traverse Left, visit Root, recursively traverse Right. For Binary Search Trees, In-order traversal yields the stored elements in strictly monotonic ascending order.
2. Pre-order traversal: Visit Root, then Left, then Right.
3. Post-order traversal: Left, Right, then Root.
