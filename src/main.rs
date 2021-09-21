use std::fs::File;
use flate2::read::GzDecoder;
use tar::Archive;
use minidom::Element;
use std::io::Read;
use anyhow::Result;
use minidom::quick_xml::Reader;

fn main() {
    let path = "test/data/test_2_runs.tar.gz";

    metadata(path);
}

fn metadata(tar_path: &str) {
    let tar_gz = File::open(tar_path).expect(&format!("Couldn't open tar file {}", tar_path));
    let tar = GzDecoder::new(tar_gz);
    let mut archive = Archive::new(tar);
    for entry in archive.entries().expect("failed to iterate XML tar.gz") {
        let mut e = entry.expect("tar gz parsing error");
        let xml_path = e.path().unwrap().to_str().unwrap().to_owned();
        if xml_path.ends_with(".sample.xml") {
            println!("{}: {}", e.path().unwrap().to_str().unwrap(), e.size());
            let mut xml = String::new();
            e.read_to_string(&mut xml).expect("Failed to read XML string");
            let mut quickxml_reader = Reader::from_str(&xml);
            // let root: Element = xml.parse().expect(&format!("Failed to parse {}",xml_path));
            let root: Element = Element::from_reader(&mut quickxml_reader).expect(&format!("Failed to parse {}",xml_path));

            /* <?xml version="1.0" encoding="UTF-8"?>
              <SAMPLE_SET xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
              <SAMPLE alias="PNUSAE002469" accession="SRS1337475">
                <IDENTIFIERS>
                  <PRIMARY_ID>SRS1337475</PRIMARY_ID>
                  <EXTERNAL_ID namespace="BioSample">SAMN04544282</EXTERNAL_ID>
                </IDENTIFIERS>
                <SAMPLE_NAME>
                  <TAXON_ID>562</TAXON_ID>
                  <SCIENTIFIC_NAME>Escherichia coli</SCIENTIFIC_NAME>
                </SAMPLE_NAME>
                <SAMPLE_LINKS>
                  <SAMPLE_LINK>
                    <XREF_LINK>
                      <DB>bioproject</DB>
                      <ID>218110</ID>
                      <LABEL>PRJNA218110</LABEL>
                    </XREF_LINK>
                  </SAMPLE_LINK>
                </SAMPLE_LINKS>
                <SAMPLE_ATTRIBUTES>
                  <SAMPLE_ATTRIBUTE>
                    <TAG>strain</TAG>
                    <VALUE>PNUSAE002469</VALUE>
                  </SAMPLE_ATTRIBUTE>
                  <SAMPLE_ATTRIBUTE>
                    <TAG>collected_by</TAG>
                    <VALUE>CDC</VALUE>
                  </SAMPLE_ATTRIBUTE>

            */
            // root.get_child("SAMPLE_NAME", namespace: NS)
            println!("{}", xml_path);
            // for child in root.children() {
            //   child.
            // }
        }
    }
}