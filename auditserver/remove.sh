#!/bin/bash

for dir in $1/*; do
    [ "$dir" = ".audit" ] && continue
    rm -rf "$dir"
done

