#!/bin/tcsh

set prompt = "% " # set prompt to avoid error from activate.csh
source env.csh

#printf "DB: %s\n" $DB

if ("$1" == "-c") then

  # continuous integration test runner
  # run with coverage, sloccount, xunit -- to be used by Hudson
  rm -rf coverage
  nosetests --with-xunit --xunit-file=.nosetests.xml --with-coverage \
    --cover-erase tests
  coverage html --include="capman/*" -d coverage
  coverage xml --include="capman/*"
  #sed 's/filename="/filename="CapMgmt\//g' coverage.xml > .coverage.xml
  #rm -f coverage.xml
  mv coverage.xml .coverage.xml
  sloccount --wide --details . > .sloccount.sc

else
  
  # default test runner, creating test.log for commits
  date |& tee test.log
  uname -a |& tee -a test.log
  
  nosetests -v tests |& tee -a test.log

endif
