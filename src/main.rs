use std::fs::File;
use flate2::read::GzDecoder;
use tar::Archive;
use std::io::Read;
use xmltree::Element;
use std::env;

fn main() {
    // let path = "test/data/test_2_runs.tar.gz";

    // metadata(path);
    metadata(&env::args().collect::<Vec<_>>()[1])
}

fn metadata(tar_path: &str) {
    let tar_gz = File::open(tar_path).expect(&format!("Couldn't open tar file {}", tar_path));
    let tar = GzDecoder::new(tar_gz);
    let mut archive = Archive::new(tar);
    for entry in archive.entries().expect("failed to iterate XML tar.gz") {
        let mut e = entry.expect("tar gz parsing error");
        let xml_path = e.path().unwrap().to_str().unwrap().to_owned();
        if xml_path.ends_with(".sample.xml") {
            // println!("{}: {}", e.path().unwrap().to_str().unwrap(), e.size());
            let mut xml = String::new();
            e.read_to_string(&mut xml).expect("Failed to read XML string");
            // let root: Element = xml.parse().expect(&format!("Failed to parse {}",xml_path));
            let mut root: Element = Element::parse(xml.as_bytes()).expect(&format!("Failed to parse {}",xml_path));

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
            let sample = root.get_mut_child("SAMPLE").expect(&format!("Cannot find SAMPLE in {}", xml_path));
            let sample_attributes1 = sample.get_mut_child("SAMPLE_ATTRIBUTES");
            if sample_attributes1.is_none() {
              eprintln!("Cannot find SAMPLE_ATTRIBUTES in {}", xml_path);
              continue;
            }
            let sample_attributes = sample_attributes1.unwrap();

            // for child in sample_attributes.child_iter()
            let run_identifier = xml_path.split("/").collect::<Vec<_>>()[0];
            // println!("{}", run_identifier);
            let mut printed_any = false;

            while let Some(unw) = sample_attributes.take_child("SAMPLE_ATTRIBUTE") {

              let tag1 = &unw.get_child("TAG");
              if tag1.is_none() {continue}
              let tag_children = &tag1.unwrap().children;
              if tag_children.len() == 0 {
                eprintln!("Bad tag_children: {:?}", tag_children);
                continue;
              }
              let tag = tag_children[0].as_text().unwrap();

              let value1 = &unw.get_child("VALUE");
              if value1.is_none() {continue}
              let value_children = &value1.unwrap().children;
              if value_children.len() == 0 {
                eprintln!("Bad value_children: {:?}", value_children);
                continue;
              }
              let value = value_children[0].as_text().unwrap();

              printed_any = true;
              println!("{}\t{}\t{}", run_identifier, tag, value);
            }

            if !printed_any {
              eprintln!("No metadata found for {}", run_identifier);
            }
        }
    }
}