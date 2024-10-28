#!/bin/zsh

has_argument() {
    [[ ("$1" == *=* && -n ${1#*=}) || ( ! -z "$2" && "$2" != -*)  ]];
}

extract_argument() {
    echo "${2:-${1#*=}}"
}

function typr() {
    zen_mode=false
    mode="dict"
    file="default"

    while [ $# -gt 0 ]; do
        case $1 in
            -t | --text)
                # handle text arg or default
                if has_argument $@; then
                    file=$(extract_argument $@)
                    shift 1
                fi
                mode="text"
                ;;
            -d | --dict)
                # handle dictionary arg or default
                if has_argument $@; then
                    file=$(extract_argument $@)
                    shift 1
                fi
                mode="dict"
                ;;
            -z | --zen)
                # dont show stats
                zen_mode=true
                ;;
            *)
                echo "Invalid option: $1"
                ;;
        esac
        shift 1
    done

    if [ "$file" = "" ]; then
        file="default"
    fi
    
    python3 ~/repos/typr/main.py $mode $file $zen_mode
}
