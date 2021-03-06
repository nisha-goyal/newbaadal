# /etc/nsswitch.conf
#
# Example configuration of GNU Name Service Switch functionality.
# If you have the `glibc-doc-reference' and `info' packages installed, try:
# `info libc "Name Service Switch"' for information about this file.

passwd: files ldap
group: files ldap
shadow: files ldap

hosts:          files mdns4_minimal [NOTFOUND=return] dns mdns4
networks:       files db

protocols:      db files ldap
services:       db files ldap
ethers:         db files
rpc:            db files

netgroup:       ldap
automount:      files ldap
