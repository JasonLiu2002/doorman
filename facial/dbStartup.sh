#!/bin/bash
echo "resetting database..."
echo "$1"
python3 reset_database.py
echo "registering users to database..."
python3 register_database.py
if [[ "$1" == "run-test" ]]
then
    echo "Running test..."
    python3 testFacial.py
fi
echo "finished!"
