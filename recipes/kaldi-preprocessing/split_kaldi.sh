#mkdir -p train test val
# find the total number of files
outpath=/data/sumit/sumit/vaani_audios_hindi/kaldi_data/junk
input_path=/data/sumit/sumit/vaani_audios_hindi/kaldi_data/original
wav_scp_path=$input_path/wav.scp
total_files=$(cat $wav_scp_path |grep wav | wc -l)
train_percent=0.8
test_percent=0.1
val_percent=0.1
# Calculate the number of files for each set
train_files=$(echo "$total_files * $train_percent" | bc)
test_files=$(echo "$total_files * $test_percent" | bc)
val_files=$(echo "$total_files * $val_percent" | bc)
total_files_calculated=$(echo "$train_files + $test_files + $val_files" | bc)
# convert into integer
train_files=${train_files%.*}
test_files=${test_files%.*}
val_files=${val_files%.*}
echo "Total files(actually): $total_files"
echo "Train files: $train_files"
echo "Test files: $test_files"
echo "Val files: $val_files"
echo "Total files(calculated): $total_files_calculated"

mkdir -p $outpath/train $outpath/test $outpath/val
cat $wav_scp_path |awk '{print $1}' |shuf |head -$train_files >$outpath/train/utt_list
cat $wav_scp_path |awk '{print $1}' |grep -Fwvf $outpath/train/utt_list > $outpath/rest_utt
cat $outpath/rest_utt |shuf |head -$test_files >$outpath/test/utt_list_test
cat $outpath/rest_utt |grep -Fwvf $outpath/test/utt_list_test > $outpath/val/utt_list_val
cd /data/sumit/sumit/codes/expts/kaldi/egs/timit/s5
./utils/subset_data_dir.sh  --utt-list $outpath/train/utt_list  $input_path  $outpath/train
./utils/subset_data_dir.sh  --utt-list $outpath/test/utt_list_test  $input_path  $outpath/test
./utils/subset_data_dir.sh  --utt-list $outpath/val/utt_list_val  $input_path  $outpath/val

# cat $wav_scp_path |awk '{print $1}' |shuf |head -$ >train_split

