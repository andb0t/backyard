#!/bin/bash

EXIT_CODE=0



# Fail if trying to commit executed jupyter notebook
 diff=$(git diff --cached | grep -e '^[\+]\s.*' | grep -e '\"execution_count\": [0-9][0-9]*')

 if [[ -z $diff ]]; then
   :
   # echo "[POLICY] Jupyter notebook test passed"
 else
   echo "[POLICY] Error: Please clear the output of the jupyter notebook before committing"
   EXIT_CODE=1
 fi



 # flake8
CHANGED_PYTHON_FILES=$(git diff --cached --name-status | grep '.py' | awk '{print $2}' |  tr '\n' ' ')
# shellcheck disable=SC2086
FLAKE_ERRORS=$(flake8 $CHANGED_PYTHON_FILES | tee)
if  [[ $FLAKE_ERRORS ]]; then
  echo "[POLICY] Error: Please make code flake8 conform before committing"
  echo "$FLAKE_ERRORS"
  EXIT_CODE=1
fi

exit $EXIT_CODE
