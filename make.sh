#! /bin/bash
# ======================================================================
# Thomas LEDUC - 13.06.2020
# ======================================================================
# PIP='python3 -m pip';
PIP='pip3';

function _clean() {
	rm --force --recursive build t4gpd.egg-info;
	find . -name __pycache__ -print0 | xargs -0 rm --force --recursive;
	find . -name \*.pyc -print0 | xargs -0 rm --force;
}

function _comment() {
	cat <<EOF;

****************************************************
***** END OF COMMAND:
***** ${1}
EOF
}

function _compile() {
	# python3 setup.py sdist bdist_wheel;
	# _comment "python3 setup.py sdist bdist_wheel";
	python3 setup.py sdist;
	_comment "python3 setup.py sdist";
}

function _coverage() {
	# GATHER THE COVERAGE DATA
	python -m coverage run -m unittest
	# GENERATE THE COVERAGE REPORT
	python -m coverage report
}

function _get_version() {
	#~ local VERSION=$(sed -ne "/^\ *return '\([^']*\)'/ {s//\1/;p;}" t4gpd/Version.py);
	local VERSION=$(sed -ne "/^\ *__version__ = '\([^']*\)'/ {s//\1/;p;}" t4gpd/_version.py);
	echo ${VERSION};
}

function _deploy() {
	local VERSION=$(_get_version);
	${PIP} install --user ./dist/t4gpd-${VERSION}.tar.gz;
	_comment "${PIP} install --user ./dist/t4gpd-${VERSION}.tar.gz";
}

function _distclean() {
	${PIP} uninstall t4gpd
	_comment "${PIP} uninstall t4gpd";
}

function _show() {
	${PIP} show t4gpd
	_comment "${PIP} show t4gpd";
}

function _twine() {
	local VERSION=$(_get_version);
	#~ twine upload ./dist/t4gpd-${VERSION}.tar.gz;
	_comment "twine upload ./dist/t4gpd-${VERSION}.tar.gz";
}

function _usage() {
	echo "Usage: $(basename ${0}) [clean|compile|coverage|deploy|distclean|help|official|show|test <dir>|twine" >& 2;
	exit 1;
}

#~ -----
case ${#} in
	0)
		_compile;;
	1) 
		case ${1} in
			clean) _clean;;
			compile) _compile;;
			coverage) _coverage;;
			deploy) _deploy;;
			distclean) _distclean;;
			show) _show;;
			twine) _twine;;
			*) _usage;;
		esac;;
	2)
		if [ "test" = ${1} ] && [ -d ${2} ]; then
			python -m unittest discover -v ${2};
		else
			_usage;
		fi;;
	*)
		_usage;;
esac
