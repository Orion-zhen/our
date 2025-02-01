export ROOT_DIR=$(pwd)
export REPO_NAME="${1:-our}"

mkdir -p $ROOT_DIR/x86_64
cd $ROOT_DIR/x86_64
repo-add --verify --sign --key $GPG_SIG_KEY $REPO_NAME.db.tar.gz *.pkg.tar.zst

rm $REPO_NAME.db
rm $REPO_NAME.db.sig
rm $REPO_NAME.files
rm $REPO_NAME.files.sig

cp $REPO_NAME.db.tar.gz $REPO_NAME.db
cp $REPO_NAME.db.tar.gz.sig $REPO_NAME.db.sig
cp $REPO_NAME.files.tar.gz $REPO_NAME.files
cp $REPO_NAME.files.tar.gz.sig $REPO_NAME.files.sig
