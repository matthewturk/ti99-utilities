for dskfn in CHI_*/*.DSK
do
    imgtool dir v9t9 ${dskfn} | awk -v dsk="$(basename $dskfn)" '{print dsk "," $1 "," $2 "," $3}' |  head -n -2 | tail -n +5
done
