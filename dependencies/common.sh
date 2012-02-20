#!/bin/bash

environment=sandbox

if [ -z $VIRTUAL_ENVS ]; then
  echo "VIRTUAL_ENVS not set."
  exit -1
fi

PREFIX=$VIRTUAL_ENVS/shared

export PATH=$PREFIX/bin:${PATH}
export LDFLAGS="-L$PREFIX/lib -L$PREFIX/lib64"


prompt() {
  package=$1
  if [[ $prompt == 'no' ]]; then
    skip='no'
  else
    echo -n "Installing $package. Continue? [Y/n] "
    read answer
    if [[ $answer == "" || $answer == "Y" || $answer == "y" ]]; then
      echo "Installing $package ..."
      skip='no'
    else
      echo "Skipping $package"
      skip='yes'
    fi
  fi
}


error() {
  package=$1
  log=$2
  echo "Error building package $package:"
  cat $2
  exit
}


install_py_tgz() {
  package=$1
  prompt $package
  if [ $skip == 'yes' ]; then
    return
  fi
  log="$PWD/$package.log"
  test -e $log && rm $log
  tar xvfz $package >> $log 2>&1 || error $package $log
  pushd $(basename $package .tar.gz) >> $log 2>&1 || error $package $log
  ### build & install command #######
  python setup.py install >> $log 2>&1 || error $package $log
  ###################################
  popd >> $log 2>&1 || error $package $log
  rm -rf $(basename $package .tar.gz)
}


install_matplotlib() {
  package=$1
  prompt $package
  if [ $skip == 'yes' ]; then
    return
  fi
  log="$PWD/$package.log"
  test -e $log && rm $log
  tar xvfz $package >> $log 2>&1 || error $package $log
  pushd $(basename $package .tar.gz) >> $log 2>&1 || error $package $log
  # add setup.cfg
  cat > setup.cfg <<EOF
[egg_info]
tag_svn_revision = 1
[directories]
basedirlist = $PREFIX
[provide_packages]
pytz = False
dateutil = False
EOF
  ### build & install command #######
  echo "Installing $package ..."
  python setup.py install >> $log 2>&1 || error $package $log
  ###################################
  popd >> $log 2>&1 || error $package $log
  rm -rf $(basename $package .tar.gz)
}


install_setuptools() {
  package=$1
  prompt $package
  if [ $skip == 'yes' ]; then
    return
  fi
  log="$PWD/$package.log"
  test -e $log && rm $log
  sh $1 >> $log 2>&1 || error $package $log
}


install_gnu_tgz() {
  package=$1
  prompt $package
  if [ $skip == 'yes' ]; then
    return
  fi
  if [ "$2" ]; then
    config_params="$2"
  fi
  log="$PWD/$package.log"
  test -e $log && rm $log
  tar xvfz $package >> $log 2>&1 || error $package $log
  pushd $(basename $package .tar.gz) >> $log 2>&1 || error $package $log
  ### build & install command #######
  ./configure --prefix=$PREFIX $config_params >> $log 2>&1 || error $package $log
  make >> $log 2>&1 || error $package $log
  make install >> $log 2>&1 || error $package $log
  ###################################
  popd >> $log 2>&1 || error $package $log
  rm -rf $(basename $package .tar.gz) >> $log 2>&1 || error $package $log
}


install_icu() {
  package=$1
  prompt $package
  if [ $skip == 'yes' ]; then
    return
  fi
  log="$PWD/$package.log"
  test -e $log && rm $log
  tar xvfz $package >> $log 2>&1 || error $package $log
  pushd icu/source >> $log 2>&1 || error $package $log
  echo "Building $package"
  ### build & install command #######
  echo "Installing $package ..."
  ./configure --prefix=$PREFIX >> $log 2>&1 || error $package $log
  make >> $log 2>&1 || error $package $log
  make install >> $log 2>&1 || error $package $log
  ###################################
  popd >> $log 2>&1 || error $package $log
  rm -rf icu
}


install_js() {
  package=$1
  prompt $package
  if [ $skip == 'yes' ]; then
    return
  fi
  log="$PWD/$package.log"
  test -e $log && rm $log
  tar xvfz $package >> $log 2>&1 || error $package $log
  pushd js/src >> $log 2>&1 || error $package $log
  echo "Building $package"
  ### build & install command #######
  echo "Installing $package ..."
  if [[ $(uname) == 'Darwin' ]]; then
    patch -p0 -i ../../patch-jsprf.c
  fi
  make BUILD_OPT=1 -f Makefile.ref >> $log 2>&1 || error $package $log
  make JS_DIST=$PREFIX BUILD_OPT=1 -f Makefile.ref export >> $log 2>&1 || error $package $log
  if [[ $(uname) == 'Darwin' ]]; then
    ranlib $PREFIX/lib/libjs.a
  fi
  ###################################
  popd >> $log 2>&1 || error $package $log
  rm -rf js
}


install_openssl() {
  package=$1
  prompt $package
  if [ $skip == 'yes' ]; then
    return
  fi
  log="$PWD/$package.log"
  test -e $log && rm $log
  tar xvfz $package >> $log 2>&1 || error $package $log
  pushd $(basename $package .tar.gz) >> $log 2>&1 || error $package $log
  ### build & install command #######
  echo "Installing $package ..."
  ./config --prefix=$PREFIX --openssldir=$PREFIX/openssl >> $log 2>&1 || error $package $log
  make >> $log 2>&1 || error $package $log
  make install >> $log 2>&1 || error $package $log
  ###################################
  popd >> $log 2>&1 || error $package $log
  rm -rf $(basename $package .tar.gz)
}


install_perfcap() {
  package=$1
  prompt $package
  if [ $skip == 'yes' ]; then
    return
  fi
  log="$PWD/$package.log"
  test -e $log && rm $log
  tar xvfz $package >> $log 2>&1 || error $package $log
  mv perfcap $PREFIX >> $log 2>&1 || error $package $log
}


install_oracle() {
  package='oracle'
  prompt $package
  if [ $skip == 'yes' ]; then
    return
  fi
  log="$PWD/$package.log"
  test -e $log && rm $log
  
  unzip instantclient-basic-linux-x86-64-11.2.0.2.0.zip >> $log 2>&1 || error $package $log
  unzip instantclient-sdk-linux-x86-64-11.2.0.2.0.zip >> $log 2>&1 || error $package $log
  rm -rf $PREFIX/oracle
  mv instantclient_11_2 $PREFIX/oracle >> $log 2>&1 || error $package $log
  export ORACLE_HOME=$PREFIX/oracle
  export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$ORACLE_HOME
  pushd $ORACLE_HOME >> $log 2>&1 || error $package $log
  cp libclntsh.so.11.1 libclntsh.so >> $log 2>&1 || error $package $log
  popd >> $log 2>&1 || error $package $log
}


packages="
python
virtualenv
couchdb
perfcap
matplotlib
oracle
sqlalchemy
"

install_pkg_python() {
  install_gnu_tgz "Python-2.7.1.tar.gz"
}


install_pkg_virtualenv() {
  if [ ! -f $PREFIX/bin/python ]; then
    install_gnu_tgz "Python-2.7.2.tar.gz"
  fi

  install_setuptools "setuptools-0.6c11-py2.7.egg"

  install_py_tgz "virtualenv-1.5.2.tar.gz"
  
  # create a virtual env
  prompt 'sandbox'
  if [ $skip == 'no' ]; then
    virtualenv --no-site-packages $VIRTUAL_ENVS/$environment
  fi
  
  . $VIRTUAL_ENVS/$environment/bin/activate
  
  py_packages="
   nose-1.0.0.tar.gz
   python-dateutil-1.4.1.tar.gz
   CouchDB-0.8.tar.gz
   simplejson-2.1.3.tar.gz
   coverage-3.4.tar.gz
  "
  
  # install python tgz packages
  for pkg in $py_packages; do
    install_py_tgz $pkg
  done
}


install_pkg_couchdb() {
  if [[ $(uname) != 'Darwin' ]]; then
    #install_openssl "openssl-1.0.0d.tar.gz"
    install_gnu_tgz "curl-7.21.4.tar.gz"
  fi
  
  # install erlang
  if [[ $(uname) == 'Darwin' ]]; then
    install_gnu_tgz "otp_src_R14B02.tar.gz" "--enable-hipe --enable-smp-support --enable-threads --enable-kernel-poll --enable-darwin-64bit"
  else
    install_gnu_tgz "otp_src_R14B02.tar.gz" "--with-ssl=/usr/include/openssl"
    #install_gnu_tgz "otp_src_R14B02.tar.gz" "--with-ssl=$PREFIX/openssl"
  fi
  
  install_icu "icu4c-4_6_1-src.tgz"
  
  # install spidermonkey
  install_js "js-1.7.0.tar.gz"
  
  # install couchdb
  install_gnu_tgz "apache-couchdb-1.0.2.tar.gz" "--with-js-include=$PREFIX/include --with-erlang=$PREFIX/lib/erlang/usr/include"
}


install_pkg_perfcap() {
  install_perfcap "perfcap_2011-11-14.tgz"
}


install_pkg_matplotlib() {
  if [ ! -f $PREFIX/bin/python ]; then
    echo "Matplotlib requires python!"
    exit -1
  fi

  . $VIRTUAL_ENVS/$environment/bin/activate

  install_py_tgz "numpy-1.5.1.tar.gz"
  install_gnu_tgz "freetype-2.4.4.tar.gz"
  install_gnu_tgz "libpng-1.4.7.tar.gz"
  install_matplotlib "matplotlib-1.0.1.tar.gz"
}


install_pkg_oracle() {
  install_oracle
}


install_pkg_sqlalchemy() {
  if [ ! -f $PREFIX/bin/python ]; then
    echo "Sqlalchemy requires python!"
    exit -1
  fi

  . $VIRTUAL_ENVS/$environment/bin/activate

  install_oracle
  install_py_tgz "cx_Oracle-5.1.tar.gz"
  # required for sqlalchemy's nosetests plugin
  install_py_tgz "pysqlite-2.6.3.tar.gz"
  install_py_tgz "SQLAlchemy-0.5.8.tar.gz"
}

