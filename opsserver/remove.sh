#!/bin/bash

for dir in $1/*; do
    [ "$dir" = ".op" ] && continue
    rm -rf "$dir"
done

