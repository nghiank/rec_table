DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source "/tmp/tensorflow/bin/activate"
pushd "$DIR/../../end_to_end/"
echo "Input:" + "$@" 
python3 rec_table.py "$@"
popd

