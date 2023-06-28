#!/bin/bash

# Wait for Redis
python functional/utils/wait_for_redis.py
python functional/utils/wait_for_redis.py

#python functional/src/t.py
# Run pytest
pytest functional/src
