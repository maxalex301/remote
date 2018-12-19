#!/bin/bash -e
if [ -z "$PUBLIC_KEY" ]; then
    echo "Please specify PUBLIC_KEY variable"
    exit 1
else
    echo $PUBLIC_KEY > /root/.ssh/authorized_keys
fi

if [ -z "$HOSTS" ]; then
    echo "You could specify HOSTS variable to create /etc/distcc/hosts"
else
    echo $HOSTS > /etc/distcc/hosts
fi

/usr/sbin/sshd -D $SSHD_PARAMS