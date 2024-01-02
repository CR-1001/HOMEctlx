#!/bin/bash

if [[ "$@" =~ ^state-group.[0-9]+ ]]; then
    echo "   3 off 240  60 100 Kitchen [9,13]"

elif [[ "$@" =~ ^state.[0-9]+ ]]; then
    echo "  10  on  80  90  50 Bedside table"

elif [[ "$@" =~ ^state-group  ]]; then
    echo "   1  on  40  90  50 Office [3,4]"
    echo "   2 off   -   -  50 Living room [1,2,7]"
    echo "   3 off 240  60 100 Kitchen [9,13]"
    echo "   5  on 120  90  80 Bedroom [10,11]"

elif [[ "$@" =~ ^state  ]]; then
    echo "   1  on  40  90  50 Couch"
    echo "   2  on   -   -  50 Table"
    echo "   3 off   -   - 100 Desk"
    echo "   4  on  40  90  80 Bookshelf"
    echo "   7  on 240  60  80 Shelf"
    echo "   9  on   -   -  30 Worktop"
    echo "  10  on  80  90  50 Bedside table"
    echo "  11 off  20  90  80 Dresser"
    echo "  13  on   -   -  30 Pantry"
fi