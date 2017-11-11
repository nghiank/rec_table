source ~/tensorflow/bin/activate
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd "$DIR/../../end_to_end/"
echo "Input:" + "$@" 
python3 rec_table.py "$@"
popd

