if (ps -u $USER -f | grep "searchd --config" | grep -v grep); then
  echo "Sphinx searchd already running."
  #echo $(ps -u $USER -f | grep "searchd" | grep -v grep)
  exit 99
fi

searchd --config /home/lucas/www/wintria.com/wintria-env/wintria.com/wintria/misc/sphinx.conf
