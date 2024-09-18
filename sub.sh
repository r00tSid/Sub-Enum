#!/bin/bash

# Function to display help
display_help() {
    echo "Usage: $0 -d <domain> | -dL <domain-list> [-o <output-file>]"
    echo
    echo "   -d <domain>         Specify a single domain to enumerate subdomains for."
    echo "   -dL <domain-list>   Specify a file containing a list of domains to enumerate."
    echo "   -o <output-file>    Specify a file to store resolved subdomains."
    echo "   -h                  Display this help message."
    exit 1
}

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python 3 is required but not installed. Please install it first."
    exit 1
fi

# Check for required arguments
if [ "$#" -lt 1 ]; then
    display_help
fi

# Default output file
output_file=""

# Parse command-line arguments
while getopts ":d:dL:o:h" opt; do
    case ${opt} in
        d)
            domain="$OPTARG"
            ;;
        dL)
            domain_list="$OPTARG"
            ;;
        o)
            output_file="$OPTARG"
            ;;
        h)
            display_help
            ;;
        \?)
            echo "Invalid option: $OPTARG" 1>&2
            display_help
            ;;
    esac
done

# Construct command
command="python3 subenum.py"

if [ -n "$domain" ]; then
    command+=" -d $domain"
elif [ -n "$domain_list" ]; then
    command+=" -dL $domain_list"
fi

if [ -n "$output_file" ]; then
    command+=" -o $output_file"
fi

# Execute the command
echo "Running subdomain enumeration..."
eval $command
