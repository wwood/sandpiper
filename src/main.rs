use std::fs::File;
use flate2::read::GzDecoder;
use tar::Archive;

fn main() {
    let path = "test/data/test_2_runs.tar.gz";

    let tar_gz = File::open(path).expect("Failed to find tar.gz file");
    let tar = GzDecoder::new(tar_gz);
    let mut archive = Archive::new(tar);
    for entry in archive.entries().expect("failed to iterate XML tar.gz") {
        let e = entry.expect("tar gz parsing error");
        println!("{}: {}", e.path().unwrap().to_str().unwrap(), e.size());
    }
}
