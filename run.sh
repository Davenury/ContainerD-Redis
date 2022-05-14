# TODO - think about default metrics

function join_by {
  local d=${1-} f=${2-}
  if shift 2; then
    printf %s "$f" "${@/#/$d}"
  fi
}

join_by , ${@:1} > result.csv
echo ",cpu" >> result.csv

for cpu in {10..100..10}
do
    echo "Performing for ${cpu}"
    echo "\tCreating container"
    sudo ctr container create --net-host --cpu-quota $((cpu*1000)) -t docker.io/library/redis:alpine redis${cpu}
    sleep 3
    echo "\tStarting task"
    sudo ctr task start -d redis${cpu}
    echo "\tPython script"
    python3 main.py $cpu ${@:1}
    echo "\tKilling task"
    sudo ctr task kill redis${cpu}
    sleep 3
    echo "\tDeleting container"
    sudo ctr container delete redis${cpu}
done

echo "Results are in results.csv file."