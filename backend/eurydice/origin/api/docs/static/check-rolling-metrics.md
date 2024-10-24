This endpoint returns information about the current state of the origin server. **Only authorized users** can access this endpoint.

It returns two types of metrics :

- **instant transferable counts**: instant values at query time ;
- **sliding window counts**: cumulative values within a specified time frame preceding the query.

Sliding window metrics time frame can be configured through the `METRICS_SLIDING_WINDOW` environment variable.
