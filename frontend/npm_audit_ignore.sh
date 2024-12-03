#!/bin/bash

# Array of CVEs to ignore
IGNORE_PACKAGES=($(jq '.name'  npm-audit-ignore-packages.json | tr -d \"))

# Run npm audit and filter out the ignored CVEs
VULNS=$(npm audit --omit=dev --json | jq -r '.vulnerabilities | to_entries[] | .key' | grep -v -E  "^($(IFS="|"; echo "${IGNORE_PACKAGES[*]}"))$" )

if [ "${#VULNS}" -gt 1 ]; then
  NB_VULNS=$(echo $VULNS | wc -w)
  echo "Packages containing vulnerabilities:" $NB_VULNS ; echo $VULNS;
  npm audit --omit=dev
  exit 1
fi

echo "No vulnerable package found"
