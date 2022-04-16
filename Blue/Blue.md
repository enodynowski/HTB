# Blue

Yet another easy difficulty HackTheBox machine. This one was particularly fast and it didn't take me much more than 10 minutes. I started off with a standard nmap tcp scan. 

```bash
nmap -sV -vv -p- -Pn -T4 <IP>
 ```

This showed me that ports 139 and 445 were open. These are the default ports for SMB. 

Between SMB running, and the name of the machine, I assumed that it was likely vulnerable to Eternal Blue. 

Running metasploit with the command ```msfconsole``` and searching for eternal blue modules with ```search eternal blue```. 

I then simply put in the IP address of the machine, my own IP address and port for the reverse shell, and then typed ```run```

This gave me a reverse shell in meterpreter. Digging through the file structure there was a user flag in C:\Users\haris\Desktop,

and a root flag in C:\Users\Administrator\Desktop. 