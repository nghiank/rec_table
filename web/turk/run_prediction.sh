DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
pushd "$DIR/../../end_to_end/"
echo "Input argument:" + "$@" 
source "/tmp/tensorflow/bin/activate" && python3 rec_table.py "$@"
popd
