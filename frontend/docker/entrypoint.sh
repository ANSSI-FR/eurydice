#!/bin/bash

set -e

# install dependencies on first start
if [ !  -d "$(pwd)/node_modules" ]; then
  make install
fi

exec "$@"
