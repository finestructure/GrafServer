set SERVERDIR="`pwd`"

set egg = env.csh

while ("$SERVERDIR" != "/")
  find "$SERVERDIR" -name $egg | grep $egg >& /dev/null
  if ($status == 0) break

  set SERVERDIR=`dirname "$SERVERDIR"`
end

setenv SERVERDIR "${SERVERDIR}"
setenv PYTHONPATH "${SERVERDIR}"

printf "SERVERDIR: %s\n" "$SERVERDIR"

if ( ! $?VIRTUAL_ENVS ) then
  setenv VIRTUAL_ENVS "$SERVERDIR/virtual_envs-`uname`"
  echo VIRTUAL_ENVS set to: $VIRTUAL_ENVS
else
  echo Using given VIRTUAL_ENVS: $VIRTUAL_ENVS
endif

if ( -f "$VIRTUAL_ENVS/sandbox/bin/activate.csh" ) then
  setenv PATH "${VIRTUAL_ENVS}/shared/bin:$PATH"
  setenv LD_LIBRARY_PATH "${VIRTUAL_ENVS}/shared/lib"
  source "${VIRTUAL_ENVS}/sandbox/bin/activate.csh"
else
  echo "Set up your virtual env by running './dependencies/install.sh virtualenv'"
endif
