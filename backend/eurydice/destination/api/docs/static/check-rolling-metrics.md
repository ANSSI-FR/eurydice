This endpoint returns information about the current state of the destination server. **Only authorized users** can access this endpoint.

It returns two types of metrics :

- **instant counts**: instant values at query time, for example instant transferable counts;
- **sliding window counts**: cumulative values within a specified time frame preceding the query.

Sliding window metrics time frame can be configured through the `METRICS_SLIDING_WINDOW` environment variable.
