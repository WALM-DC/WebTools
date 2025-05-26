f:
cd "F:\WebTools\AktionspreisFixer"
python JsonList.py
echo "Push new List.Json to git."
PAUSE
cd "F:\WebTools\public"
git push
PAUSE