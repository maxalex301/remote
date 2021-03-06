#!/bin/bash -e
if [ -z "$PUBLIC_KEY" ]; then
    echo "Please specify PUBLIC_KEY variable"
    exit 1
else
    echo $PUBLIC_KEY > /root/.ssh/authorized_keys
fi

echo $DISTCC_HOSTS >> /root/.distcc/hosts

/usr/sbin/sshd -D $SSHD_PARAMS