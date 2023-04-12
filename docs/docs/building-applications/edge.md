# Using Groundlight on the edge

Starting your model evaluations at the edge reduces latency, cost, network bandwidth, and energy. Once you have downloaded and installed your Groundlight edge models, you can configure the Groundlight SDK to use your edge environment by configuring the 'endpoint' to point at your local environment as such:

```python
from groundlight import Groundlight
gl = Groundlight(endpoint="http://localhost:6717")
```

(Edge model download is not yet generally available.  Work with your Solutions Engineer to set up edge inference.)
