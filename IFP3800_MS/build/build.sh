#!/bin/sh

. ./setting.sh
#°ÑÐÎÈç20110804µÄÈÕÆÚ¸ñÊ½¸³Öµ¸ø»·¾³±äÁ¿DATE
export DATE=`date +%Y%m%d`

echo "==============================================================="
echo checkout files from svn

rm -Rf ./ifpms
mkdir ./ifpms
svn checkout ${svn_url} ./ifpms
cd ./ifpms
#È¡³ösvnÖ´ÐÐ½á¹ûÖÐµÄRevisionÐÐ£¬°ÑRevision: xxÌæ»»Îªxx¼´È¡³öÎªsvnµÄÐÞ¶©ºÅ£¬×îºó¸³Öµ¸ø±äÁ¿BUILD.
export BUILD=`svn info | grep Revision: | sed 's/Revision: //g'`
#Ìõ¼þÅÐ¶ÏÓï¾äµÄÁ½±ß¸÷ÒªÓÐÒ»¸ö¿Õ¸ñ£¬svn info·µ»ØÖÐÎÄÐÅÏ¢Ê±£¬ÅÐ¶ÏºóÌáÈ¡°æ±¾ºÅ.
if [  "$BUILD" == ""  ]; then
    export BUILD=`svn info | grep '^版本:' | sed 's/版本: //g'`
fi	
echo "var appver='v1.2-r${BUILD}-b${DATE}' ;" > ./chrome/content/ver.js
find . -name .svn | xargs -i rm -Rf {}

if [ $js_min -eq 1 ]; then
echo "js script minifing..."
jsfiles=`find ./chrome/content -name "*.js" | grep -v min.js | grep -v config.js `
pyfiles=`find ./extensions/ifpms@ov-orange.com  -name "*.py" | grep -v ifpms.py | grep -v userifpms.py`
for js in $jsfiles
#ÕÒ³öcontentÄ¿Â¼ÒÔ.js½áÎ²£¬µ«ÅÅ³ýmin.jsµÄÎÄ¼þ£¬Öð¸öÑ¹Ëõºó£¬Çå³ýÔ´ÎÄ¼þ£¬ÔÙ°ÑÉú³ÉµÄÎÄ¼þ¸Ä³ÉºÍÔ´ÎÄ¼þÍ¬ÃûµÄÎÄ¼þ£¬ÊµÏÖµÄÔ´ÎÄ¼þµÄ²»¸ÄÃûÑ¹Ëõ¡£

do
	echo "$js minifing..."
    java -jar ../yuicompressor-2.4.6.jar --type js -o  ${js}.out $js
	if [ $? -eq 0 ]; then
		mv ${js}.out $js
	else
		rm -rf ${js}.out
	fi
done
fi

python -m compileall ./extensions/ifpms@ov-orange.com/pylib
find ./extensions/ifpms@ov-orange.com/pylib -name "*.py" | grep -v ifpms.py | grep -v mark.py | grep -v userifpms.py | xargs -i rm -Rf {}

cd ./chrome
jar -cvfM ifpms.jar content locale skin
if [ $? -ne 0 ]; then
	echo " command not found"
	exit
fi
rm -rf ./content ./locale ./skin
cd ..


for skin_item in default gsd
do
    cp license.${skin_item}.txt chrome/license.txt
    echo "content ifpms jar:ifpms.jar!/content/" > chrome/chrome.manifest
    echo "content etc etc/" >> chrome/chrome.manifest
    echo "content wav wavs/" >> chrome/chrome.manifest
    echo "content sample sample/" >> chrome/chrome.manifest
    echo "content mapImg mapImg/" >> chrome/chrome.manifest
    echo "skin ifpms default jar:ifpms.jar!/skin/${skin_item}/" >> chrome/chrome.manifest
    echo "locale ifpms zh-CN jar:ifpms.jar!/locale/zh-CN/" >> chrome/chrome.manifest
    echo "locale ifpms en-US jar:ifpms.jar!/locale/en-US/" >> chrome/chrome.manifest
	
    rm extensions/ifpms@ov-orange.com/pylib/mark.py
    echo "#!/usr/bin/env python" >> extensions/ifpms@ov-orange.com/pylib/mark.py
    echo "# -*- coding: UTF8 -*-" >> extensions/ifpms@ov-orange.com/pylib/mark.py
    echo "logo = '${skin_item}'" >> extensions/ifpms@ov-orange.com/pylib/mark.py
   
    if [ ${skin_item} == 'default' ]; then
	    cp ../setup.nsi .
		makensis setup.nsi	
        mv setup-v1.2-r${BUILD}-b${DATE}.exe ../ifpms-v1.2-r${BUILD}-b${DATE}.exe
		rm setup.nsi
    else
        if [ ! -f "$ifpms.exe" ]; then
            mv ifpms.exe gsd.exe
        fi
		cp ../gsdsetup.nsi .
		makensis gsdsetup.nsi
        mv setup-v1.2-r${BUILD}-b${DATE}.exe ../${skin_item}-v1.2-r${BUILD}-b${DATE}.exe
		rm gsdsetup.nsi
    fi
done
cd ..
echo "Job Done!"
