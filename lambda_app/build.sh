#!/bin/bash

dir_here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
dir_site_packages="${dir_here}/site-packages"

bin_pip="pip3.8"

#echo ${dir_site_packages}
rm -r "${dir_site_packages}"
${bin_pip} install -r "${dir_here}/requirements.txt" -t "${dir_site_packages}"

cd "${dir_site_packages}" || exit
zip "${dir_here}/deploy.zip" * -r -9 -q
