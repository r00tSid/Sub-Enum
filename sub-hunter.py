import requests
import sys
import pyfiglet

# For printing ascii bannwr
figlet= pyfiglet.figlet_format("SUB-HUNTER")
print(figlet)
print("\n*******************************************************")
print("\n*         Copyright of sidhanta palei,2022            *")
print("\n*      https://github.com/Sidhant0703/Port-hunter     *")
print("\n*******************************************************")
#Main program code
sub_list=open("wordlist.txt").read()
subs=sub_list.splitlines()
for sub in subs:
    sub_domain=f"http://{sub}.{sys.argv[1]}"
    try:
        requests.get(sub_domain)
    except requests.ConnectionError:
        pass
    else:
         print("Valid Domain:",sub_domain)