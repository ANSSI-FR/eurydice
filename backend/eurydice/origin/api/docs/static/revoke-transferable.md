You can revoke an outgoing transferable waiting to be processed (*PENDING*) or currently being transferred (*ONGOING*).
Any ongoing transfer for this transferable will be interrupted, its data will be deleted from both origin and destination storage, and the transferable will be removed from the queue (giving way to awaiting transferables).

Please note that a transferable cannot be revoked using this API endpoint if it is still being submitted, nor if it is already fully transferred.

