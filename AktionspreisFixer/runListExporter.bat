@echo off
echo Pull ICOM git?
PAUSE
c:
cd "C:\xxxlutz\IG-Creator\XXXLutz\ICOM"
git pull

echo Create new List.json.
PAUSE
f:
cd "F:\WebTools\AktionspreisFixer"
python JsonList.py

echo Push new List.Json to git.
PAUSE
f:
cd "F:\WebTools\public"
git add .
git commit -m "3D Modellist Update"
git push origin
PAUSE