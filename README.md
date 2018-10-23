# pySSH
Send & execute a command or script to a remote host.


### Examples
Grep hosts `192.168.1.19` & `192.168.1.3` application log files for `VARIABLE`.
```bash
./ssh.py \
  --hostname 192.168.1.19 192.168.1.3 \
  --username user99 \
  --commands "grep VARIABLE /var/log/application/"
```
Copy the script `test.sh` to the host `192.168.1.19`, execute and delete it afterwards.
```bash
./ssh.py \
  --hostname 192.168.1.19 \
  --username user99 \
  --script test.sh \
  --destination /home/user99/test.sh \
  --delete
```
Copy the script `test.sh` to the host `192.168.1.1` using the given key and execute it.
```bash
./ssh.py \
  --hostname 192.168.1.1 \
  --username user99 \
  --script test.sh \
  --key ~/.ssh/some.pem \
  --destination /home/user99/test.sh \
```
