#!/bin/bash

# file: genXBMfonts.sh
# brief: generate font glyphs and C header file from XBM images
# author: 2015, masterzorag@gmail.com
# changes: 2018 bhgv.empire@gmail.com

# This script uses ImageMagick convert to generate images of glyphs

# 1. rebuild $fontDestDir/xbm_font.h
# ./genXBMfonts.sh razor.ttf 16

# 2. use generated XBM fonts: hardcode in xbm_print
# cp out/razor* <the-path-where-it-should-be>

# 3. rebuild xbm_tools
# make clean && make


if [ -z $1 ]; then
    echo "$0 Font Font_H"
    echo "$0 razor.ttf 16"
    exit
fi

### arguments, keep 16 as default

Font=$1
Font_H=$2

### process argv end here ###

# ImageMagick supported extension: pnm, png, bmp, xpm, pbm... here we deal with xbm
type=xbm

# for each font
if [ -r "$Font" ]
then
    Font=$Font
else
    Font=$Font".ttf"
fi

echo $Font

if [ -r "$Font" ]
then
    fn=$(echo "$Font" | grep -o -P "\w+\." | grep -o -P "\w+")

    fontDestDir="./out"
    xpmDestDir=$fontDestDir"/"$fn

    mkdir -p "$fontDestDir"
    mkdir -p "$xpmDestDir"

    th=$fontDestDir/temp.h
    tc1=$fontDestDir/temp1.c
    tc2=$fontDestDir/temp2.c
    outh=$fontDestDir/"$fn"_xbm_font.h
    outc=$fontDestDir/"$fn"_xbm_font.c

    if [ -f "$th" ]
    then
        rm $th $tc1 $tc2
        rm $outh $outc
    fi

    # keep track of array index
    n="0"

    echo > $th
    echo "#define NULL (void*)0" >> $th
    echo >> $th
    echo "typedef struct {char ascii; unsigned char w; unsigned char h; char *bits;} xbm_font;" >> $th
    echo >> $th
    echo >> $th

    echo > $tc1
    echo > $tc2

    echo "extern xbm_font font_"$fn"_"$Font_H"[];" >> $th

    echo "const xbm_font font_"$fn"_"$Font_H"[] = {" >> $tc2

    # chars="  ! a b c d e f g h i j k l m n o p q r s t u v w x y z 0 1 2 3 4 5 6 7 8 9 + - / # . , \*"    
    # for c in $chars
    # Better: do a printable range set, start from char ' ' (space): ASCII 32
    # ASCII 127 is NOT printable and will write output.h file in binary form!
    # keep it under 127 for now...
    for c in `seq 32 126`
    do
        #printf "%d\t\x%x\n" $c $c

        # compose decimal representation and label
        d="$(printf %.3d $c)"                    #printf "\x$(printf %x $c)"
        D="$(printf "\x$(printf %x $c)")"

        # Generate (x Font_H) images, 1bpp of each character in ASCII range 
        # call imagemagick tool to convert bitmap
        convert \
        +antialias \
        -depth 1 -colors 2 \
            -size x"$Font_H" \
            -quality 100 \
            -background white -fill black \
            -font "$Font" \
            -pointsize 17 \
            -density 72 \
            -gravity center \
            label:$D \
            "$xpmDestDir/_"$d"."$type &> /dev/null

        # 2. check to build data bits
        if [ -f "$xpmDestDir/_"$d"."$type ]
        then
            # 1. build commented label header: array idx, ascii code, glyph

            echo "#include \""$fn"/_"$d"."$type"\"" >> $tc1
            
            echo "  { "$c" ,_"$d"_width, _"$d"_height, _"$d"_bits, }, /* $n: ASCII $d [$D] */" >> $tc2

            echo "$n: $d.$type [$D]"

            # extra: dump single XBM to console
#            ./xbm_dump "$fontDestDir/$d.$type"
        else
            # 1. build zeroed commented label header: array idx, ascii code, glyph
            echo "  { "$c", 0, 0, NULL, }, /* $n: ASCII $d [$D] */" >> $tc2

            echo "$n: $d.$type does not exists!"
        fi

        # increase array count
        ((n+=1))

    done

    echo "};" >> $tc2

    printf "I: range of %d ASCII codes\n" $n

    # 1. build top C header
    printf "#ifndef __XBM_FONT_H_%s__\n" $fn > $outh
    printf "#define __XBM_FONT_H_%s__\n" $fn >> $outh

    printf "\n/*\n\t%s bits\n" $fonts >> $outh
    printf "\tgenerated with genXBMfonts, https://github.com/masterzorag/xbm_tools\n" >> $outh
    printf "\t2015, masterzorag@gmail.com\n*/\n\n" >> $outh

    printf "#define LOWER_ASCII_CODE %d\n" 32 >> $outh
    printf "#define UPPER_ASCII_CODE %d\n" $((n + 32)) >> $outh
    printf "#define FONT_H %d\n" $Font_H >> $outh
    printf "#define BITS_IN_BYTE %d\n\n" 8 >> $outh
    echo >> $outh

    cat $th >> $outh
    echo  >> $outh
    printf "#endif //__XBM_FONT_H__\n" >> $outh

    cat $tc1 > $outc
    echo >> $outc
    echo >> $outc
    echo "#include \""$fn"_xbm_font.h\"" >> $outc
    echo >> $outc
    echo >> $outc
    cat $tc2 >> $outc

    # extra: cleanup from temp
    rm $tc1 $tc2 $th
fi


# count and report exported
n=$(ls $fontDestDir/*.$type | wc -l)
printf "I: succesfully parsed %d ASCII codes\nDone\n\n" $n

# inquiry
#file $outc

# extra: look at exported XBM(s)
#viewnior $fontDestDir &> /dev/null

exit
