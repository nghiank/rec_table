DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "$DIR/../../tensorflow/bin/activate"
pushd "$DIR/../../end_to_end/"
echo "Input:" + "$@" 
python3 rec_table.py "$@"
popd

