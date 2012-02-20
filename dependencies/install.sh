#!/bin/bash

if [[ -z $SERVERDIR ]]; then
  echo "SERVERDIR not set."
  exit -1
fi

source $(dirname $0)/common.sh

usage() {
	echo `basename $0`: ERROR: $* 1>&2
	echo usage: `basename $0` '[-f] [db|dev]' 1>&2
	exit 1
}

promt='yes'

while getopts ":fgh" flag
do
  case "$flag" in
    f) prompt='no';;
    h) usage; exit;;
    ?) usage; exit;;
  esac
done

shift $((OPTIND-1))


if [ "$#" -eq 0 ]
then
  echo Packages: $packages
  exit
fi

for package in "$@"
do
  case "$package" in
    *)
      pushd $SERVERDIR/dependencies > /dev/null 2>&1
      install_pkg_$package
      popd > /dev/null 2>&1
      ;;
  esac
done
echo Make to run 'source env.ch' again!

