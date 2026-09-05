"""Centralized Topic and Academic Domain Classification."""
from enum import Enum


class TopicDomain(str, Enum):
    DATA_STRUCTURES = "data_structures"
    RECURSION = "recursion"
    MACHINE_LEARNING = "machine_learning"
    SORTING_ALGORITHMS = "sorting_algorithms"
    PROGRAMMING = "programming"
    PHYSICS_ELECTRONICS = "physics"
    MATHEMATICS = "mathematics"
    GENERAL = "general"


def classify_topic(topic: str = "", concept: str = "") -> TopicDomain:
    """
    Classifies a topic or concept string into a structured TopicDomain enum.
    Evaluates specialized domains with strict keyword precedence to prevent false-positive leakage.
    """
    combined = f"{topic} {concept}".lower().strip()
    if not combined:
        return TopicDomain.GENERAL

    # 1. Machine Learning & Neural Networks (Highest precedence for AI/ML terms)
    ml_keywords = [
        "neural network",
        "neural networks",
        "forward pass",
        "deep learning",
        "perceptron",
        "activation function",
        "weights and biases",
        "backpropagation",
        "gradient descent",
        "machine learning",
        "loss function",
        "hidden layer",
        "neuron",
        "neurons",
        "convolutional",
        "recurrent neural",
        "transformer",
        "llm",
        "relu",
        "sigmoid",
        "softmax",
    ]
    if any(kw in combined for kw in ml_keywords):
        return TopicDomain.MACHINE_LEARNING

    # 2. Recursion & Call Stacks
    recursion_keywords = [
        "recursion",
        "recursive",
        "call stack",
        "base case",
        "stack frame",
        "tail recursion",
        "divide and conquer",
    ]
    if any(kw in combined for kw in recursion_keywords):
        return TopicDomain.RECURSION

    # 3. Sorting Algorithms
    sorting_keywords = [
        "merge sort",
        "quick sort",
        "bubble sort",
        "insertion sort",
        "selection sort",
        "heap sort",
        "radix sort",
        "binary search",
        "sorting algorithm",
    ]
    if any(kw in combined for kw in sorting_keywords):
        return TopicDomain.SORTING_ALGORITHMS

    # 4. Physics & Electronics
    physics_keywords = [
        "circuit",
        "circuits",
        "ohm",
        "voltage",
        "current",
        "resistance",
        "resistor",
        "electricity",
        "kirchhoff",
        "capacitance",
        "force",
        "gravity",
        "velocity",
        "thermodynamics",
        "newton",
    ]
    if any(kw in combined for kw in physics_keywords):
        return TopicDomain.PHYSICS_ELECTRONICS

    # 5. Data Structures (Explicit tree, graph, heap, and list structures)
    ds_keywords = [
        "binary tree",
        "binary trees",
        "binary search tree",
        "bst",
        "avl",
        "red-black",
        "binary heap",
        "min-heap",
        "max-heap",
        "linked list",
        "doubly linked list",
        "tree traversal",
        "in-order",
        "pre-order",
        "post-order",
        "b-tree",
        "trie",
        "adjacency matrix",
    ]
    if any(kw in combined for kw in ds_keywords):
        return TopicDomain.DATA_STRUCTURES

    # Standalone tree/graph/heap data structures
    words = combined.split()
    if any(w in words for w in ["tree", "trees", "graph", "graphs", "heap", "heaps"]):
        return TopicDomain.DATA_STRUCTURES

    # 6. Mathematics
    math_keywords = [
        "calculus",
        "derivative",
        "integral",
        "linear algebra",
        "matrix multiplication",
        "eigenvalue",
        "probability",
        "statistics",
        "geometry",
        "trigonometry",
        "equation",
        "formula",
    ]
    if any(kw in combined for kw in math_keywords):
        return TopicDomain.MATHEMATICS

    # 7. Programming & Software Engineering
    programming_keywords = [
        "python",
        "javascript",
        "typescript",
        "syntax",
        "loop",
        "while loop",
        "for loop",
        "variable",
        "object-oriented",
        "oop",
        "class",
        "classes",
        "inheritance",
        "async",
        "pointer",
    ]
    if any(kw in combined for kw in programming_keywords):
        return TopicDomain.PROGRAMMING

    return TopicDomain.GENERAL
