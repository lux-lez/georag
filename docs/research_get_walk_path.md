<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" class="logo" width="120"/>

# How can I get the best walking path between two points?

To get the **best walking path between two points using OpenStreetMap data in Python**, the standard method is to use the **OSMnx** library, which retrieves street networks and finds optimal routes based on real walking paths. Here is a step-by-step guide to accomplish this:

**1. Install OSMnx:**

```bash
pip install osmnx
```

**2. Download the Walking Street Network for Your Area:**

```python
import osmnx as ox

# Example: Berlin as the area of interest
place = "Berlin, Germany"
G = ox.graph_from_place(place, network_type='walk', simplify=True)
```

This downloads and constructs a *networkx* graph of walkable streets.

**3. Get Your Origin and Destination Coordinates:**

```python
origin_lon, origin_lat = 13.4050, 52.5200   # Example coordinates
dest_lon, dest_lat = 13.3889, 52.5170
```

**4. Snap Points to the Nearest Network Nodes:**

```python
orig_node = ox.nearest_nodes(G, origin_lon, origin_lat)
dest_node = ox.nearest_nodes(G, dest_lon, dest_lat)
```

This ensures you are routing *from and to* actual nodes in the street network[^2][^6].

**5. Compute the Shortest Walking Path:**

```python
route = ox.shortest_path(G, orig_node, dest_node, weight='length')  # use 'length' for physical distance
```

For other metrics (like travel time at a set walking speed), see step 7.

**6. (Optional) Visualize or Export the Route:**

```python
import matplotlib.pyplot as plt

ox.plot_graph_route(G, route)
```

Or, to get the coordinates:

```python
nodes = ox.graph_to_gdfs(G, edges=False)
route_nodes = nodes.loc[route]
coords = list(zip(route_nodes['y'], route_nodes['x']))  # (lat, lon) pairs
```

**7. (Optional) Calculate Walking Time Instead of Distance:**
By default, the cost ("weight") is the physical distance (in meters).

- To compute time instead, you must assign a walking speed to each edge and set the edge's "travel_time" attribute.
- OSMnx has helper functions for adding edge speeds and travel times[^3][^9]:

```python
G = ox.add_edge_speeds(G, hwy_speeds={})  # let OSMnx infer reasonable speeds for footways etc.
G = ox.add_edge_travel_times(G)
route = ox.shortest_path(G, orig_node, dest_node, weight='travel_time')
```

- To enforce a fixed walking speed (e.g., 4 km/h), you can edit edge attributes manually (see search result for detailed methods)[^3][^4].

**Key Libraries and Functions:**


| Step | Function |
| :-- | :-- |
| Download walk network | `ox.graph_from_place(..., network_type='walk')` |
| Snap to nodes | `ox.nearest_nodes()` |
| Shortest path | `ox.shortest_path(..., weight='length')` or `weight='travel_time'` |
| Visualize | `ox.plot_graph_route()` |
| Edge speeds/travel time | `ox.add_edge_speeds()`, `ox.add_edge_travel_times()` |

**References:**

- For a deep dive, see the [OSMnx documentation][^5][^9] and sample notebooks.
- A full practical example is at Towards Data Science and other search results[^2][^3][^6].

This method robustly gives you the **best walking route based on real-world pedestrian paths**, accounting for actual network topology and optionally travel times.

<div style="text-align: center">⁂</div>

[^1]: https://lenkahas.com/post/pandana.html

[^2]: https://towardsdatascience.com/shortest-path-dijkstras-algorithm-step-by-step-python-guide-896769522752/

[^3]: https://stackoverflow.com/questions/74431736/how-can-i-calculate-walk-and-cycle-times-with-osmnx

[^4]: https://gis.stackexchange.com/questions/448334/how-to-calculate-the-length-and-duration-of-trip-for-a-geodataframe-of-points-on

[^5]: https://osmnx.readthedocs.io/en/stable/user-reference.html

[^6]: https://towardsdatascience.com/shortest-path-algorithm-with-osm-walking-network-6d2863ae96be/

[^7]: https://github.com/eemilhaa/walkability-analysis

[^8]: https://geoffboeing.com/2016/11/osmnx-python-street-networks/

[^9]: https://osmnx.readthedocs.io/en/stable/getting-started.html

