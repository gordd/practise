#!/bin/sh -x

# we may have an encrypted foofile for us that may be a new letsencrypt dir
# 20190802 gd creation
# 20200118 gd turn down the noise a little, houseclean, and check results 
# 20201325 gd down a little more
# 20200516 gd apparently, gpg won't overwrite an existing file (since march 16th?)
# 20200716 gd make postfix and dovecot restart so they re-read the new cert

# Expected crontab should be something like:
# 16  4   *   *   *       cd /etc/letsencrypt;tar -jcf /safe/today.tgz * ;sha1sum /safe/today.tgz | /usr/bin/tee -a /safe/today.log; /safe/update_cert.sh

OLDFILE=/today.tgz
NEWFILE=/foofile
OLDDIR=/root/olddir
NEWDIR=/root/foodir
EXTDIR=/home/carrierp

# if [it] exists and size>0 and not dir|device and not link
if [ -e ${EXTDIR}${NEWFILE} -a -s ${EXTDIR}${NEWFILE} -a -f ${EXTDIR}${NEWFILE} -a ! -L ${EXTDIR}${NEWFILE} ]; then
	/bin/cp -fP ${EXTDIR}${NEWFILE} ${NEWDIR}${NEWFILE} 
	echo $0: found ${EXTDIR}${NEWFILE} and coping it to ${NEWDIR}${NEWFILE} 
else
	echo $0: could not find ${EXTDIR}${NEWFILE} 
	exit 1

fi

# gpg won't overwrite an existing file?
/bin/rm -f ${NEWDIR}${OLDFILE} 
WHY=`/usr/bin/gpg --batch --output ${NEWDIR}${OLDFILE} --decrypt ${NEWDIR}${NEWFILE} 2>&1` 

if [ $? -ne 0 ]; then
	echo $0: gpg failed saying $WHY
	exit 2
fi

all=$(sha1sum ${OLDDIR}${OLDFILE} )
ORIG=${all%% *}
all=$(sha1sum ${NEWDIR}${OLDFILE} )
NEW1=${all%% *}
echo $0: old $ORIG new $NEW1

# bug: if the ORIG doesn't exist, sh complains: + [ = a9ac ] update_cert.sh: 37: [: =: unexpected operator
# doesn't work. lets fall off the fi: if [ -e ${ORIG} -a ${ORIG} = ${NEW1} ]; then

if [ ${ORIG} = ${NEW1} ]; then
	echo $0: already applied the update, so no need to do anything
	exit 0
fi

#DSTDIR=${NEWDIR}/etc/letsencrypt
DSTDIR=/etc/letsencrypt
DATE=$(/bin/date +"%Y%m%d")
echo $0 move the old one ${DSTDIR} into ${DSTDIR}.${DATE}

# the real business
/bin/mv ${DSTDIR} ${DSTDIR}.${DATE}
/bin/mkdir ${DSTDIR}
(cd ${DSTDIR};/bin/tar -xvf ${NEWDIR}${OLDFILE} )

# check for the existance of the live fullchain
FULLCHAIN=${DSTDIR}/live/emmanueluc.ca/fullchain.pem
if [ -e ${FULLCHAIN} ]; then
	# now we can mark the update as successfully done.
	/bin/cp -r ${NEWDIR}${OLDFILE} ${OLDDIR}${OLDFILE} 
	echo $0: successful update of ${DSTDIR}
	# kick the main users of the certificates to make them reread
	/usr/sbin/service postfix restart
	/usr/sbin/service dovecot restart
fi

	service dovecot restart
exit 0
