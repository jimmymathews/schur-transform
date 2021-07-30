#!/bin/bash

FOUND_VERSION_CHANGE=0
FOUND_ANOTHER_CHANGE=0
git status -s |
{
while IFS= read -r line
  do
    is_modified_file=$(echo "$line" | grep -oE '^ M ')
    if [[ "$is_modified_file" == ' M ' ]]; then
        if [[ "$line" == ' M schurtransform/version.txt' ]]; then
            FOUND_VERSION_CHANGE=1
        else
            FOUND_ANOTHER_CHANGE=1
        fi
    fi

    is_added_file=$(echo "$line" | grep -oE '^A[M ] ')
    if [[ "$is_added_file" != "" ]]; then
        FOUND_ANOTHER_CHANGE=1
    fi
done

if [[ ( "$FOUND_VERSION_CHANGE" == "1" ) && ( "$FOUND_ANOTHER_CHANGE" == "1" ) ]]; then
    echo "Version has changed, but found another change. Not ready to autorelease."
    exit
fi

if [[ ( "$FOUND_VERSION_CHANGE" == "0" ) ]]; then
    echo "Version has not changed, so not ready to autorelease. Maybe you need one last commit."
    exit
fi

if [[ ( "$FOUND_VERSION_CHANGE" == "1" ) && ( "$FOUND_ANOTHER_CHANGE" == "0" ) ]]; then
    echo "Ready to autorelease; version is updated, and everything else is the same."
    echo "<autoreleasing...>"
fi
}
