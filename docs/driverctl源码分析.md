

![](image/Pasted%20image%2020230522212140.png)


```
#!/bin/bash

confdir=/etc/driverctl.d
bus=${SUBSYSTEM:-pci}
probe=1
save=1
debug=0

declare -A devclasses
devclasses=(["all"]=""
            ["storage"]="01"
            ["network"]="02"
            ["display"]="03"
            ["multimedia"]="04"
            ["memory"]="05"
            ["bridge"]="06"
            ["communication"]="07"
            ["system"]="08"
            ["input"]="09"
            ["docking"]="0a"
            ["processor"]="0b"
            ["serial"]="0c"
)

function log()
{
    echo "driverctl: $*" >&2
}

function debug()
{
    [ "$debug" -ne 0 ] && log "$@"
}

function error()
{
    log "$@"
    exit 1
}

function usage()
{
    echo "Usage: driverctl [OPTIONS...] {COMMAND}..."
    echo
    echo "Inspect or control default device driver bindings."
    echo
    echo "Supported commands:"
    echo "  set-override <device> <driver>    Make <driver> the default driver"
    echo "                                    for <device>"
    echo "  unset-override <device>           Remove any override for <device>"
    echo "  load-override <device>            Load an override previously specified"
    echo "                                    for <device>"
    echo "  list-devices                      List all overridable devices"
    echo "  list-overrides                    List all currently specified overrides"
    echo
    echo "Supported options:"
    echo " -h --help             Show this help"
    echo " -v --verbose --debug  Show verbose debug information"
    echo " -b --bus <bus>        Work on bus <bus> (default pci)"
    echo "    --noprobe          Do not reprobe when setting, unsetting, or"
    echo "                       loading an override"
    echo "    --nosave           Do not save changes when setting or unsetting"
    echo "                       an override"
    echo ""
}

function unbind()
{
    if [ -L "$syspath/driver" ]; then
        debug "unbinding previous driver $(basename "$(readlink "$syspath/driver")")"
        if ! echo "$dev" > "$syspath/driver/unbind"; then
            error "unbinding $dev failed"
        fi
    else
        debug "device $dev not bound" 
    fi
}

function probe_driver()
{
    debug "reprobing driver for $dev"
    echo "$dev" > "/sys/bus/$bus/drivers_probe"
}

function save_override()
{
    debug "saving driver override for $dev"
    if [ -n "$drv" ]; then
	[ -d "$confdir" ] || mkdir -p "$confdir"
        echo "$drv" > "$confdir/$sddev"
    else
        rm -f "$confdir/$sddev"
    fi
}

function list_devices()
{
    devices=()
    for d in "/sys/bus/$bus/devices"/*; do
        if [ -f "$d/driver_override" ]; then
            override="$(< "$d/driver_override")"
            if [ "$1" -eq 1 ] && [ "$override" == "(null)" ]; then
                continue
            fi
          
            line="$(basename "$d")"
            devices+=("$line")

            if [ -n "$2" ]; then
                class="$(< "$d/class")"
                [ "$2" == "${class:2:2}" ] || continue
            fi
            if [ -L "$d/driver" ]; then
                line+=" $(basename "$(readlink "$d/driver")")"
            else
                line+=" (none)"
            fi
            if [ "$1" -ne 1 ] && [ "$override" != "(null)" ]; then
                line+=" [*]"
            fi

            if [ $debug -ne 0 ]; then
                line+=" ($(udevadm info -q property "$d" | grep ID_MODEL_FROM_DATABASE | cut -d= -f2))"
            fi
            echo "$line"
        fi
    done
    if [ ${#devices[@]} -eq 0 ]; then
        error "No overridable devices found. Kernel too old?"
    fi
}

function set_override()
{
    if [ ! -f "$syspath/driver_override" ]; then
        error "device does not support driver override: $dev"
    fi
    if [ -n "$drv" ] && [ "$drv" != "none" ]; then
        debug "setting driver override for $dev: $drv"
        if [ ! -d "/sys/module/$drv" ]; then
            debug "loading driver $drv"
            /sbin/modprobe -q "$drv" || error "no such module: $drv"
        fi
    else
        debug "unsetting driver override for $dev"
    fi
    unbind
    echo "$drv" > "$syspath/driver_override"

    if [ "$drv" != "none" ] && [ $probe -ne 0 ]; then 
        probe_driver
        if [ ! -L "$syspath/driver" ]; then
            error "failed to bind device $dev to driver $drv"
        fi
    fi
}

while (($# > 0)); do
    case ${1} in
    --noprobe)
        probe=0
        ;;
    --nosave)
        save=0
        ;;
    --debug|--verbose|-v)
        debug=1
        ;;
    -b|--bus)
        bus=${2}
        shift
        ;;
    -h|--help|-*)
        usage
        exit 0
        ;;
    set-override)
        if [ $# -ne 3 ]; then
            usage
            exit 1
        fi

        cmd=$1
        dev=$2
        drv=$3
        break
        ;;
    load-override|unset-override)
        if [ $# -ne 2 ]; then
           usage
           exit 1
        fi

        cmd=$1
        dev=$2
        break
        ;;
    list-devices|list-overrides)
        if [ $# -gt 2 ]; then
            usage
            exit 1
        fi

        if [ -n "$2" ] && [ ! "${devclasses[$2]+_}" ]; then
            error "device type must be one of: ${!devclasses[*]}"
        fi
        cmd=$1
        devtype="${devclasses[${2:-all}]}"
        break
        ;;
    *)
        usage
        exit 1
        ;;
    esac
    shift
done

if [ -z "$cmd" ]; then
    usage
    exit 1
fi

if [ -n "$dev" ]; then
        case ${dev} in
        */*)
            bus=${dev%%/*}
            dev=${dev#*/}
            ;;
        esac
        if [ -n "${DEVPATH:-}" ]; then
            devpath="$DEVPATH"
        else
            devlink="/sys/bus/$bus/devices/$dev"
            [ -L "$devlink" ] || error "no such device: $dev"
            devpath=$(realpath "$devlink" | cut -c5-)
        fi
        syspath="/sys/$devpath"
        sddev="$bus-$dev"
fi

case ${cmd} in
    load-override)
        if [ -s "$confdir/$sddev" ]; then
            drv=$(< "$confdir/$sddev")
	    set_override "$dev" "$drv"
        else
            exit 1
        fi
        ;;
    list-devices)
        list_devices 0 "$devtype"
        ;;
    list-overrides)
        list_devices 1 "$devtype"
        ;;
    set-override)
        set_override "$dev" "$drv"
        if [ $save -ne 0 ]; then
           save_override
        fi

        ;;       
    unset-override)
        set_override "$dev" ""
        if [ $save -ne 0 ]; then
           save_override
        fi
        ;;
esac

```