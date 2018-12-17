#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd "$SCRIPT_DIR/.."

MODULE=""
if [ -z "$1" ]; then
    echo "No argument supplied! What module do you want to create?"
    echo "[analyzer, scanner]"
    exit
else
    MODULE="$1"
fi

MODULE_NAME=""
if [ -z "$2" ]; then
    echo "No name supplied! What should the module be called?"
    echo "[YOUR_NAME]"
    exit
else
    MODULE_NAME="$2"
fi

TARGET_DIR="modules/$MODULE_NAME"
SOURCE_DIR="templates/$MODULE/example"

echo "Create new $MODULE module $MODULE_NAME in $TARGET_DIR ..."
mkdir -p $TARGET_DIR
cp -r "$SOURCE_DIR"/* "$TARGET_DIR"

echo "Rename files and folders ..."
mv "$TARGET_DIR"/src/backyard/module/example "$TARGET_DIR"/src/backyard/module/"$MODULE_NAME"

echo "Set up git submodule ..."
SUBMODULE_PATH="$TARGET_DIR/src/backyard/api/proto"
rm -r "$SUBMODULE_PATH"
git submodule add --force git@github.com:cyber-fighters/proto.git "$SUBMODULE_PATH"

echo "Register new $MODULE ..."
NEW_FILE="src/backyard/supervisor/config/$MODULE.d/$MODULE_NAME.yaml"
cp "src/backyard/supervisor/config/$MODULE.d/example.yaml" "$NEW_FILE"
sed -i 's/id: "EXAMPLE"/id: "'$MODULE_NAME'"/g' "$NEW_FILE"
sed -i 's/'$MODULE'-example/'$MODULE'-'$MODULE_NAME'/g' "$NEW_FILE"

echo "Manual steps:"
echo " - modify $NEW_FILE to represent the new $MODULE and its dependencies"
echo " - implement your new $MODULE in $TARGET_DIR/src/backyard/module/$MODULE_NAME/__main__.py"
