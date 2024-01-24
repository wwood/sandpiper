<template>
  <div>
    <section class="section is-small container has-text-justified">
      <h1 class="title">Team</h1>
      <p>This website, and SingleM itself, is the result of a collaboration between (in no particular order) <a href="https://research.qut.edu.au/cmr/team/ben-woodcroft/">Ben Woodcroft</a>, Rossen Zhao, Mitchell Cunningham, Joshua Mitchell, Samuel Aroney, <a href="https://findanexpert.unimelb.edu.au/profile/753413-linda-blackall">Linda Blackall</a>, <a href="https://research.qut.edu.au/cmr/team/gene-tyson/">Gene Tyson</a>, <a href="https://www.alberdilab.dk/members">Raphael Eisenhofer</a> and <a href="https://www.alberdilab.dk/members">Antton Alberdi</a>.</p><br />
      <p>Most of us are at the <a href="https://research.qut.edu.au/cmr/">Centre for Microbiome Research</a>, School of Biomedical Sciences, Queensland University of Technology (<a href="qut.edu.au">QUT</a>), Translational Research Institute, Woolloongabba, Australia. Mitchell Cunningham and Linda Blackall are at the School of BioSciences, The University of Melbourne, Victoria, Australia. Raphael Eisenhofer and Antton Alberdi are at the Centre for Evolutionary Hologenomics, Globe Institute, University of Copenhagen, Denmark.</p>
    </section>

    <section class="section is-small container has-text-justified">
      <h1 class="title">Bulk download</h1>
      <p>Community profiles for all runs are available for download from <a href="https://zenodo.org/doi/10.5281/zenodo.10547493">Zenodo</a>.</p><br />
      <p>Please feel free to get in touch with <a href="https://research.qut.edu.au/cmr/team/ben-woodcroft/">us</a> if you have any questions or comments, or want data of other kinds.</p>
    </section>

    <section class="section is-small container has-text-justified">
      <h1 class="title">How Sandpiper {{ version }} was built</h1>
      <p>The data underlying Sandpiper was generated using the <a href="https://github.com/wwood/singlem">SingleM</a> pipeline, applied to public metagenome datasets listed in the <a href="https://www.ncbi.nlm.nih.gov/sra">NCBI SRA</a> that were designated as metagenomic, or derived from "metagenomic" organisms such as "soil metagenome". This list of public metagenomes which was generated on {{ scrape_date }}.</p><br />

      <p>SingleM is a tool to find the abundances of discrete operational taxonomic units (OTUs) directly from shotgun metagenome data, without heavy reliance on reference sequence databases. It operates by scanning for reads that cover highly conserved regions of single copy marker genes (35 bacterial, 37 archaeal, 59 total) when translated into amino acids. The nucleotides from each read that cover these conserved gene sections are then clustered into operational taxonomic units (OTUs). Importantly, this clustering happens before the taxonomy of the cluster is determined, setting it apart from methods which rely more heavily on reference databases. With SingleM, multiple OTUs can be assigned to one taxa, indicating e.g. strain heterogeneity within a species, or multiple families from a novel taxa.</p><br />

      <p>The OTU tables generated for each marker gene are then combined ("condensed") into a single taxonomic profile, representing the read coverage of each taxa in the metagenome. From this read coverage, relative abundance is found by dividing the read coverage of each taxa by the total read coverage of the metagenome. This relative abundance is then used to generate the Sandpiper visualisations.</p><br />

      <h2 class="title is-5">Community profiling</h2>
      <p>These raw SingleM taxonomic profiles, which contain OTUs derived from the 59 genes, are available for download from each run's page. However, for ease of interpretation and search, runs on this website are usually represented as a 'condensed' profile. These condensed profiles are a unified version of the profiles derived from each marker gene, so there is only one profile to inspect (instead of 59), though condensed profiles collapse the OTUs from each taxon into a single group.</p><br />

      <p>For more complicated analyses, such as searching for OTUs that cannot be easily isolated through their taxonomy (e.g. if they are novel), a more bespoke search procedure might be more appropriate. These kinds of analyses cannot currently be done on the sandpiper website, but in such cases please <a :href="'mailto:'+decode('o.jbbqpebsg@dhg.rqh.nh')">get in touch</a> with us.</p><br />

      <h2 class="title is-5">SingleM Microbial Fraction (SMF)</h2>
      <p>To estimate the number of reads in each metagenome which are either bacterial or archaeal, the <a href="https://wwood.github.io/singlem/tools/microbial_fraction">microbial_fraction</a> (SMF) mode of SingleM was used. SMF bases its estimate on the coverage of each taxon in the SingleM community profile, the genome lengths of those taxons, and the total size of the metagenome. It does not rely on mapping reads to non-microbial reference genomes.</p><br />

      <h2 class="title is-5">Prediction of whether the metagenome is associated with a eukaryotic host</h2>
      <p>Each metagenome was predicted as either host-associated or ecological based upon a machine learning algorithm (an <a href="https://xgboost.ai/">XGBoost</a> one achieving ~93% accuracy), using the "organism" metadata field recorded at NCBI as the target for prediction, and the taxonomic profile as the input data. Metagenomes are either classified as "eukaryote host-associated" or "ecological". Host-associated samples are recorded or predicted to be under the <a href="https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=410656">organismal metagenome</a> NCBI taxonomy, ecological ones are all others. We anticipate that predictions based on microbial community profiles will become an increasingly important method for characterising microbiomes in the future, and we hope that future versions of this website will provide more detailed predictions about each community.</p><br />

      <h2 class="title is-5">Metadata corrections</h2>
      <p>Sandpiper uses data from the <a
      href="https://www.ncbi.nlm.nih.gov/sra">NCBI SRA</a> and associated
      databases to add metadata to each sequence dataset. Many times, this
      metadata is incorrect, vague or missing. If you notice something like
      this, we are collecting and correcting them in <a
      href="https://github.com/wwood/public_sequencing_metadata_corrections">public
      repository</a>. Any corrections submitted there (or submitted directly upstream e.g. to
      NCBI) are appreciated.</p><br />

    </section>

    <section class="section is-small container has-text-justified">
      <h1 class="title">Changelog</h1>
      <h2 class="title is-5">v0.2.1</h2>
        <div class="columns has-text-left"> 
          <div class="column content">  
            <ul> 
              <li>Added links to bulk download of condensed profiles.</li>
            </ul> 
          </div> 
        </div>
      <h2 class="title is-5">v0.2.0</h2>
      <div class="columns has-text-left"> 
        <div class="column content"> 
          <ul>
            <li>Updated to use SingleM 0.16.0, changing the species assignment and "condense" procedures</li>
            <li>Added "SMF" (SingleM Microbial Fraction) statistics</li>
            <li>Community profile and SMF data: originally generated from SRA metadata collected Dec 15, 2021, using git commit of SingleM e97d171 and metapackage 'S3.metapackage_20211101.smpkg. Then renewed with SingleM v0.16.0 using metapackage S3.2.1.GTDB_r214.metapackage_20231006.smpkg.</li>
            <li>Community profiles can be downloaded in bulk from <a href="https://zenodo.org/doi/10.5281/zenodo.10547493">Zenodo</a>.</li>
          </ul>
        </div> 
      </div>
    </section>

    <section class="section is-small container has-text-justified">
      <h1 class="title">Acknowledgements</h1>
      <p>Development of Sandpiper and SingleM was funded through Australian Research Council Future Fellow (#FT210100521), Discovery Project (#DP230101171) and Discovery Early Career Research Award (#DE160100248) grants, as well as the <a href="https://emerge-bii.github.io/">EMERGE</a> National Science Foundation (NSF) Biology Integration Institute (#2022070) and Genomic Science Program of the United States Department of Energy (DOE) Office of Biological and Environmental Research (BER), grants DE-SC0004632, DE-SC0010580 and DE-SC0016440. Cloud computing was generously contributed by Amazon Web Services (AWS) and Google Cloud (GCP).</p>
      <br />
      <p>The sandpiper background image on the front page was derived from <a href="https://www.flickr.com/photos/snarfel/11631543856/in/pool-birds_birds_birds">Frans Vandewalle</a> (CC-NC).</p>
    </section>
  </div>
</template>

<script>
import { fetchSandpiperStats } from '@/api'

export default {
  name: 'About',
  title: 'About - Sandpiper',
  data: function () {
    return {
      num_terrabases: null,
      num_runs: null,
      num_bioprojects: null,
      version: null,
      scrape_date: null
    }
  },
  created () {
    // fetch the data when the view is created and the data is
    // already being observed
    this.fetchData()
  },
  methods: {
    fetchData () {
      fetchSandpiperStats()
        .then(response => {
          const r = response.data
          this.num_terrabases = r.num_terrabases
          this.num_runs = r.num_runs
          this.num_bioprojects = r.num_bioprojects
          this.version = r.version
          this.scrape_date = r.scrape_date
        })
    },

    decode (a) {
      // ROT13 : a Caesar cipher 
      // letter -> letter' such that code(letter') = (code(letter) + 13) modulo 26
      return a.replace(/[a-zA-Z]/g, function(c){
        return String.fromCharCode((c <= "Z" ? 90 : 122) >= (c = c.charCodeAt(0) + 13) ? c : c - 26);
      })
    }
  },
  watch: {
    // call again the method if the route changes
    $route: 'fetchData'
  }
}
</script>
