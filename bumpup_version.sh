#!/bin/sh

usage() {
    cat << EOF
Usage: `basename $0` NEW_VERSION
EOF
    exit $1
}

[ "$#" -ne "1" ] && usage

NEW_VERSION="$1"

sed -i -e "s/^version *= *'.*'$/version = '$NEW_VERSION'/" setup.py
sed -i -e "s/^__version__ *= *'.*'$/__version__ = '$NEW_VERSION'/" alnair/__init__.py
echo "Please write changes in $NEW_VERSION to CHANGES.rst"
