#!/bin/bash

# Default values
GhidraAnalyze="/home/pi/apps/ghidra_10.4_PUBLIC/support/analyzeHeadless"
ProjectDir="/home/pi/apps/decompile/res_dll/ghidra_project"
ProjectName="res_dll"
InputFile="/home/pi/apps/decompile/res_dll/PapyRes.dll"
ScriptsDir="/home/pi/apps/decompile/ghidra"
PreScripts=("ghidra_create_segment_pre.py")
PostScripts=("ghidra_export_helpers.py" "ghidra_decompile_list.py")
NoNewWindow=false
ShowCommand=false

# Function to build argument list
function build_argument_list {
    local projDir="$1"
    local projName="$2"
    local inputFile="$3"
    local scriptsDir="$4"
    local preScripts="$5"
    local postScripts="$6"

    args=()
    args+=("$projDir" "$projName")

    if [ -n "$inputFile" ]; then
        args+=("-import" "$inputFile")
    fi
    
    if [ -n "$scriptsDir" ]; then
        args+=("-scriptPath" "$scriptsDir")
    fi

    for s in $preScripts; do
        args+=("-preScript" "$s")
    done

    for s in $postScripts; do
        args+=("-postScript" "$s")
    done

    echo "${args[@]}"
}

# Parse command-line parameters
while [[ $# -gt 0 ]]; do
    case $1 in
        -GhidraAnalyze)
            GhidraAnalyze="$2"
            shift; shift
            ;;
        -ProjectDir)
            ProjectDir="$2"
            shift; shift
            ;;
        -ProjectName)
            ProjectName="$2"
            shift; shift
            ;;
        -InputFile)
            InputFile="$2"
            shift; shift
            ;;
        -ScriptsDir)
            ScriptsDir="$2"
            shift; shift
            ;;
        -PreScripts)
            shift
            PreScripts=()
            while [[ $# -gt 0 && "$1" != -* ]]; do
                PreScripts+=("$1")
                shift
            done
            ;;
        -PostScripts)
            shift
            PostScripts=()
            while [[ $# -gt 0 && "$1" != -* ]]; do
                PostScripts+=("$1")
                shift
            done
            ;;
        -NoNewWindow)
            NoNewWindow=true
            shift
            ;;
        -ShowCommand)
            ShowCommand=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Build argument list
args=$(build_argument_list "$ProjectDir" "$ProjectName" "$InputFile" "$ScriptsDir" "${PreScripts[@]}" "${PostScripts[@]}")

if [ "$ShowCommand" = true ]; then
    echo "AnalyzeHeadless command: \"$GhidraAnalyze\" $args"
fi

echo "Running analyzeHeadless:"
echo "  exe: $GhidraAnalyze"
echo "  project: $ProjectDir / $ProjectName"
echo "  input: $InputFile"
echo "  scripts: $ScriptsDir"

# Run the Ghidra analyzer
if [ "$NoNewWindow" = true ]; then
    "$GhidraAnalyze" $args
else
    exec "$GhidraAnalyze" $args
fi

# Check for success
if [ $? -ne 0 ]; then
    echo "Failed to start analyzeHeadless."
    exit 1
else
    echo "analyzeHeadless finished."
fi

