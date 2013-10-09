#/bin/sh

THRESHOLD=15

T=$( (time timeout 20s wget -p --no-cache --delete-after cualbondi.com.ar -q) 2>&1 >/dev/null | grep real | awk -F"[m\t]" '{ printf "%s\n", $2*60+$3 }')
COND=$( awk "BEGIN{print ($T>$THRESHOLD)?1:0 }" )

if [ "$COND" = "1" ]; then
    echo "restarting nginx"
    /usr/bin/service nginx restart
fi
