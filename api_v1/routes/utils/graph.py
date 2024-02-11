"""
The module allows you to create an arbitrary weighted graph,
has methods for traversing the graph in depth and width, a method
for searching for a Hamiltonian cycle
"""

from __future__ import annotations
from typing import Any, Iterable, Tuple, Set
from queue import Queue
from random import choice


class Node:
    """node class storing node value and incident edges"""

    def __init__(self, value: Any) -> None:
        self.value = value
        self.edges = set()
        self.parents = {}

    def __ne__(self, other: Node) -> bool:
        if not isinstance(other, type(self)):
            return True

        return self.value != other.value

    def __eq__(self, other: Node) -> bool:
        if not isinstance(other, type(self)):
            return False

        return self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        return f"{self.value}"


class Edge:
    """edge class storing the incident node"""

    def __init__(self, incident_node: Node, weight: int) -> None:
        self.incident_node = incident_node
        self.weight = weight

    def __lt__(self, other: Edge) -> bool:
        return self.weight < other.weight

    def __repr__(self) -> str:
        return f"<Edge: weight={self.weight}, incident_node={self.incident_node}>"


class GraphBase:
    def add_or_get_node(self, value: Any) -> Node:
        raise NotImplementedError

    def traverse(self, *, how: str) -> None:
        raise NotImplementedError


class MatrixGraph(GraphBase):
    def __init__(self):
        raise NotImplementedError

    def add_or_get_node(self, value: Any) -> Node:
        raise NotImplementedError

    def traverse(self, *, how: str) -> None:
        raise NotImplementedError


class HashTableGraph(GraphBase):
    """an undirected graph class implemented through a dictionary"""

    def __init__(self, data_input: Iterable[Tuple[Any, Any, int]]) -> None:
        self.graph = {}
        self.n_vertex = 0

        for from_, to_, weight in data_input:
            node = self.add_or_get_node(from_)
            incident_node = self.add_or_get_node(to_)

            edge = Edge(incident_node, weight)

            node.edges.add(edge)
            incident_node.parents[node] = edge

    def add_or_get_node(self, value: Any) -> Node:
        """adding and returning a node"""

        if value not in self.graph:
            self.graph[value] = Node(value)
            self.n_vertex += 1

        return self.graph[value]

    def delete_node(self, value: Any) -> None:
        raise NotImplementedError

    def delete_edge(self, value_from: Any, value_to: Any) -> None:
        """
        :param value_from:
        :param value_to:
        """
        if value_from not in self.graph:
            raise KeyError(f"the graph does not contain vertices with the value={value_from}")

        if value_to not in self.graph:
            raise KeyError(f"the graph does not contain vertices with the value={value_from}")

        node_from = self.graph[value_from]
        node_to = self.graph[value_to]

        edge = node_to.parents[node_from]
        node_from.edges.remove(edge)
        node_to.parents.pop(node_from)

    def traverse(self, *, how: str = "dfs") -> None:
        """
        wrapper for traversing all nodes of the graph.
        :param how: graph traversal algorithm, values: ``bfs``, ``dfs`` or ``rdfs``
        """
        how = how.lower()
        if how == "bfs":
            traverse_ = self._bfs
        elif how == "dfs":
            traverse_ = self._dfs_without_recur
        elif how == "rdfs":
            traverse_ = self._dfs_with_recur
        else:
            raise ValueError("invalid argument value")

        passed = set()
        for node in self.graph.values():
            if node not in passed:
                traverse_(node, passed)

    @staticmethod
    def _bfs(node: Node, passed: Set[Node]) -> None:
        """breadth-first traversal with queue"""

        queue = Queue()
        queue.put(node)
        while not queue.empty():
            node = queue.get()
            passed.add(node)
            print(node)
            for edge in node.edges:
                if edge.incident_node not in passed:
                    queue.put(edge.incident_node)
                    passed.add(edge.incident_node)

    @staticmethod
    def _dfs_without_recur(node: Node, passed: Set[Node]) -> None:
        """depth-first traversal without recursion"""

        stack = [node]
        while stack:
            node = stack[-1]
            if node not in passed:
                print(node)
                passed.add(node)
            has_children = False
            for edge in node.edges:
                if edge.incident_node not in passed:
                    stack.append(edge.incident_node)
                    has_children = True
                    break
            if not has_children:
                stack.pop()

    def _dfs_with_recur(self, node: Node, passed: Set[Node]) -> None:
        """depth-first traversal with recursion"""

        print(node.value)
        passed.add(node)
        for edge in node.edges:
            if edge.incident_node not in passed:
                self._dfs_with_recur(edge.incident_node, passed)


class HamiltonianGraph(HashTableGraph):
    def _ore_theorem(self) -> bool:
        """verifies Ore's theorem"""

        if self.n_vertex < 3:
            return False

        for node1 in self.graph.values():
            for node2 in self.graph.values():
                if node1 != node2 and \
                    node2 not in node1.parents and \
                    node1 not in node2.parents and \
                        len(node1.edges) + len(node2.edges) < self.n_vertex:

                    return False

        return True

    @staticmethod
    def _get_weight_between_nodes(node: Node, adjacent_node: Node) -> int:
        """return weight between adjacent nodes"""

        if adjacent_node in node.parents:
            return node.parents[adjacent_node].weight

        if node in adjacent_node.parents:
            return adjacent_node.parents[node].weight

        raise ValueError("nodes are not adjacent")

    @staticmethod
    def _get_nearest_not_passed_node(node: Node, passed: Set[Node]) -> Node:
        """returns the nearest unmarked node"""

        edges_to_not_passed_nodes = filter(
            lambda edge: edge.incident_node not in passed,
            node.edges)

        edge_to_nearest_node = min(edges_to_not_passed_nodes)

        return edge_to_nearest_node.incident_node

    def find_hamiltonian_cycle(
            self, *, start_value: Any = None, accuracy: int = 0
    ) -> (str, dict):
        """finds a suboptimal Hamiltonian cycle"""

        data = {
            "route": [],
            "total duration": 0
        }
        if not self._ore_theorem():
            msg = "There is no way"
            return msg, data

        if start_value is None:
            start_node = choice(list(self.graph.values()))
        elif start_value in self.graph:
            start_node = self.graph[start_value]
        else:
            raise KeyError(f"The graph does not contain vertices with this value={start_value}")

        data["route"].append({
            "node": f"{start_node}",
            "duration": 0
        })

        cur_node = start_node
        passed = {cur_node}

        while len(passed) < self.n_vertex:
            nearest_node = self._get_nearest_not_passed_node(cur_node, passed)
            duration = self._get_weight_between_nodes(nearest_node, cur_node)
            data["route"].append({
                "node": f"{nearest_node}",
                "duration": duration
            })
            data["total duration"] += duration
            passed.add(nearest_node)
            cur_node = nearest_node

        duration = self._get_weight_between_nodes(start_node, cur_node)
        data["route"].append({
            "node": f"{start_node}",
            "duration": duration
        })
        data["total duration"] += duration
        msg = "The shortest path has been successfully found"

        return msg, data