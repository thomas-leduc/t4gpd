#! /bin/bash
# ======================================================================
# Thomas LEDUC - 13.06.2020
# ======================================================================
# PIP='python3 -m pip';
PIP='pip3';

function _clean() {
	rm --force --recursive build t4gpd.egg-info;
	find . -name __pycache__ | xargs rm --force --recursive;
}

function _comment() {
	cat <<EOF;

****************************************************
***** END OF COMMAND:
***** ${1}
EOF
}

function _compile() {
	python3 setup.py sdist bdist_wheel;
	_comment "python3 setup.py sdist bdist_wheel";
}

function _get_version() {
	local VERSION=$(sed -ne "/^\ *return '\([^']*\)'/ {s//\1/;p;}" t4gpd/Version.py);
	echo ${VERSION};
}

function _copy_sam() {
	local VERSION=$(_get_version);
	cp ./dist/t4gpd-${VERSION}.tar.gz ~/Dropbox/crenau/7_encadrements/sam.mailly/dev;
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

function _usage() {
	echo "Usage: $(basename ${0}) [clean|compile|deploy|distclean|help|sam|show]" >& 2;
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
			deploy) _deploy;;
			distclean) _distclean;;
			sam) _copy_sam;;
			show) _show;;
			*) _usage;;
		esac;;
	*)
		_usage;;
esac
