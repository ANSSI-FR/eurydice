This endpoint lists user's incoming transferables, including both those already received and those still being received.

Please note the estimated time of arrival is only displayed on the origin-side API.
This is because it is calculated in real time based on information the destination-side API does not know.

To navigate through the pages, request the previous, current and next page identifiers (found in the API's response) like so : `GET /api/v1/transferables/?page={identifier of the page you want}`.

If new transferables are received while you are browsing with page identifiers, they won't be displayed in results but the new_items indicator will be set to true.
You can then request the first page again, without the page query parameter, to see them.

N.B. While the standard way to explore transferables is to use the previous, current and next page identifiers from responses, you can also use the more advanced syntax and jump arbitrary amounts of pages via `GET /api/v1/transferables/?delta={positive or negative amount of pages}&from={any page identifier}`.
