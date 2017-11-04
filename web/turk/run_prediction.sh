echo "aaaaaaaaaaaaaaaaaaaaaaaaaInput:" + "$@" 
source ~/tensorflow/bin/activate
pushd ../../end_to_end/
echo "Input:" + "$@" 
python3 rec_table.py "$@"
popd

