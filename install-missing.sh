#!/bin/bash

# Map containers to their requirements files
declare -A container_reqs=(
  ["fraud_django"]="requirements/django.txt"
  ["fraud_fastapi"]="requirements/fastapi.txt"
  ["fraud_ml"]="requirements/ml.txt"
)

for container in "${!container_reqs[@]}"; do
    req_file=${container_reqs[$container]}

    echo "🔹 Checking container $container against $req_file ..."

    # Copy requirements file into container temporarily
    docker cp "$req_file" "$container":/tmp/reqs.txt

    # Install missing packages only
    docker exec -it "$container" bash -c "
        echo 'Installing missing packages...'
        pip install --upgrade pip
        pip install --requirement /tmp/reqs.txt || true
        # Freeze current environment
        pip freeze > /tmp/current.txt
    "

    # Compare and append only missing packages to original requirements file
    docker exec -it "$container" bash -c "
        comm -13 <(sort /tmp/reqs.txt) <(sort /tmp/current.txt) > /tmp/missing.txt
    "
    docker cp "$container":/tmp/missing.txt ./missing.txt

    if [ -s ./missing.txt ]; then
        echo "Adding new packages to $req_file ..."
        cat ./missing.txt >> "$req_file"
        sort -u "$req_file" -o "$req_file"
    else
        echo "✅ No new packages to add for $container."
    fi

    rm -f ./missing.txt
done

echo "🎉 All done!"
