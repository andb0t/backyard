#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd "$SCRIPT_DIR/.."

MODULE=""
INPUT_INFO="Usage: $0 [analyzer, scanner] YOUR_NAME"

if [ -z "$1" ]; then
    echo "No argument supplied! $INPUT_INFO"
    exit
else
    if [ "$1" == "scanner" ] || [ "$1" == "analyzer" ]; then
      MODULE="$1"
    else
      echo "What module do you want to create?"
      echo "$INPUT_INFO"
      exit
    fi

fi

MODULE_NAME=""
if [ -z "$2" ]; then
    echo "No name supplied! What should the module be called?"
    echo "$INPUT_INFO"
    exit
else
    MODULE_NAME="$2"
fi

TARGET_DIR="modules/$MODULE/$MODULE_NAME"
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
echo "docker build -t backyard/$MODULE-$MODULE_NAME:latest $TARGET_DIR" >> "$SCRIPT_DIR"/build_containers.sh
sed -i 's/backyard.module.example/backyard.module.'$MODULE_NAME'/g' "$TARGET_DIR"/Dockerfile
sed -i 's/backyard.module.example/backyard.module.'$MODULE_NAME'/g' "$TARGET_DIR"/setup.py

echo "Manual steps:"
echo " - modify $NEW_FILE to represent the new $MODULE and its dependencies"
echo " - implement your new $MODULE in $TARGET_DIR/src/backyard/module/$MODULE_NAME/__main__.py"
