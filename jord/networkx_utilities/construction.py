import osmnx
import shapely
from draugr.numpy_utilities import positive_int_hash
from networkx import MultiDiGraph, MultiGraph
from typing import Any, Mapping

__all__ = [
    "assertive_add_edge",
    "IllegalLoopException",
    "IllegalDuplicateEdgeException",
    "assertive_add_shapely_node",
    "network_to_osm_xml",
    "compute_node_id",
]

from warg import ensure_existence, recursive_flatten

from jord import PROJECT_APP_PATH


class IllegalLoopException(Exception): ...


class IllegalDuplicateEdgeException(Exception): ...


def assertive_add_edge(
    graph: MultiGraph,
    u: int,
    v: int,
    key: int,
    attributes: Mapping[str, Any],
    *,
    allow_loops: bool = True,
    allow_duplicates: bool = False,
) -> None:
    """

    :param graph: The Graph
    :type graph: MultiDiGraph
    :param u: from node id
    :type u: int
    :param v: to node id
    :type v: int
    :param key: id of edge
    :type key: int
    :param attributes: attributes of edge
    :type attributes: Mapping[str, Any]
    :param allow_loops: Allow loops
    :type allow_loops: bool
    :param allow_duplicates: Allow duplicate edges
    :type allow_duplicates: bool
    :return: None
    """
    if not allow_loops:
        if u == v:
            raise IllegalLoopException(f"{u} == {v}")

    assert isinstance(u, int), f"{u=} is not int, but {type(u)=}"
    assert isinstance(v, int), f"{v=} is not int, but {type(v)=}"

    assert graph.has_node(u)
    assert graph.has_node(v)

    if not allow_duplicates and graph.has_edge(u, v, key):
        if graph.has_edge(u, v, key):
            raise IllegalDuplicateEdgeException(
                f"Graph already contains the edge ({u} -> {v}) with {key=}"
            )

    graph.add_edge(u, v, key=key, **attributes)


def assertive_add_shapely_node(
    graph: MultiDiGraph, u: int, point: shapely.Point, **kwargs
) -> None:
    """
    Add a shapely point based node to the graph.


    :param graph: The Graph
    :type graph: MultiDiGraph
    :param u: Node id
    :type u: int
    :param point:
    :type point: shapely.Point
    :param kwargs: Attributes of node
    :return: None
    """
    assert isinstance(u, int)

    graph.add_node(
        u,
        x=float(point.x),
        y=float(point.y),
        # id=u,
        **kwargs,
    )


def network_to_osm_xml(network: MultiDiGraph) -> bytes:
    osm_cache_path = ensure_existence(PROJECT_APP_PATH.site_cache) / "to_upload.osm"

    edge_tags = set(recursive_flatten([edge.keys() for edge in network.edges.values()]))
    node_tags = set(recursive_flatten([node.keys() for node in network.nodes.values()]))

    osmnx.settings.useful_tags_way = edge_tags
    osmnx.settings.useful_tags_node = node_tags

    osmnx.save_graph_xml(G=network, filepath=osm_cache_path)

    with open(osm_cache_path, "rb") as f:
        return f.read()


def compute_node_id(point: shapely.geometry.Point) -> int:
    return positive_int_hash(
        ",".join(str(c) for c in (point.x, point.y, point.z if point.has_z else None))
    )
