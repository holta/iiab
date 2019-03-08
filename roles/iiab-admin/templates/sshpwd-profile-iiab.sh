#!/bin/bash

export TEXTDOMAIN=Linux-PAM

. gettext.sh

# bash syntax "function check_user_pwd() {" was removed, as it prevented all
# lightdm/graphical logins (incl autologin) on Raspbian: #1252 -> PR #1253
check_user_pwd() {
    # $meth (hashing method) is typically '6' which implies 5000 rounds
    # of SHA-512 per /etc/login.defs -> /etc/pam.d/common-password
    meth=$(sudo grep "^$1:" /etc/shadow | cut -d: -f2 | cut -d$ -f2)
    salt=$(sudo grep "^$1:" /etc/shadow | cut -d: -f2 | cut -d$ -f3)
    hash=$(sudo grep "^$1:" /etc/shadow | cut -d: -f2 | cut -d$ -f4)
    [ $(python3 -c "import crypt; print(crypt.crypt('$2', '\$$meth\$$salt'))") == "\$$meth\$$salt\$$hash" ]
}

# Credit to the folks at the Raspberry Pi Foundation
check_hash() {
    if ! id -u iiab-admin > /dev/null 2>&1 ; then return 0 ; fi
    if grep -q "^PasswordAuthentication\s*no" /etc/ssh/sshd_config ; then return 0 ; fi
    if check_user_pwd "iiab-admin" "{{ iiab_admin_published_pwd }}"; then
        echo
        echo $(/usr/bin/gettext "SSH is enabled and the published password for user 'iiab-admin' is in use.")
        echo $(/usr/bin/gettext "THIS IS A SECURITY RISK - please run 'sudo passwd iiab-admin' to change it.")
        echo
     fi
}

systemctl is-active {{ sshd_service }} > /dev/null && check_hash
unset check_hash
