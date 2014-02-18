if (ps -u $USER -f | grep "searchd --config" | grep -v grep); then
  echo "Sphinx searchd already running."
  #echo $(ps -u $USER -f | grep "searchd" | grep -v grep)
  exit 99
fi
#echo 'running it'
searchd --config ~/webapps/windjango/Wintria/misc/sphinx.conf
