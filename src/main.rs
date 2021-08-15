use std::fs::File;
use flate2::read::GzDecoder;
use tar::Archive;
use minidom::Element;
use std::io::Read;
use std::io::Error;

fn main() {
    let path = "test/data/test_2_runs.tar.gz";

    metadata(path).unwrap();
}

/* d2 = d[Platform=='ILLUMINA' & LibrarySource=='METAGENOMIC' & LibrarySelection=='RANDOM'][bases>100e6 & bases<200e9]

Platform = ILLUMINA means an ILLUMINA entry in <EXPERIMENT_SET><EXPERIMENT>:
    <PLATFORM>
      <ILLUMINA>
        <INSTRUMENT_MODEL>Illumina HiSeq 2000</INSTRUMENT_MODEL>
      </ILLUMINA>
    </PLATFORM>

LibrarySource and Library selection in <EXPERIMENT_SET><EXPERIMENT>:
      <LIBRARY_DESCRIPTOR>
        <LIBRARY_NAME>C6s</LIBRARY_NAME>
        <LIBRARY_STRATEGY>WGS</LIBRARY_STRATEGY>
        <LIBRARY_SOURCE>METAGENOMIC</LIBRARY_SOURCE>
        <LIBRARY_SELECTION>RANDOM</LIBRARY_SELECTION>

bases in run.xml - nope it isn't. Annoying.
*/
fn metadata(tar_path: &str) -> Result<(), Error> {
    // 

    let tar_gz = File::open(tar_path)?;
    let tar = GzDecoder::new(tar_gz);
    let mut archive = Archive::new(tar);
    for entry in archive.entries().expect("failed to iterate XML tar.gz") {
        let mut e = entry.expect("tar gz parsing error");
        let xml_path = e.path().unwrap().to_str().unwrap().to_owned();
        if xml_path.ends_with(".run.xml") {
            println!("{}: {}", e.path().unwrap().to_str().unwrap(), e.size());
            let mut xml = String::new();
            e.read_to_string(&mut xml);
            let root: Element = xml.parse()?;
        }

        
    }
    Ok(())
}