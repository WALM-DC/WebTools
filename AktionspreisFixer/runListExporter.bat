@echo off
echo Pull ICOM git.
c:
cd "C:\xxxlutz\IG-Creator\XXXLutz\ICOM"
git pull

echo Create new List.json.
f:
cd "F:\WebTools\AktionspreisFixer"
python JsonList.py

echo Push new List.Json to git.
PAUSE
cd "F:\WebTools\public"
git push
PAUSE