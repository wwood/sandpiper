#!/usr/bin/env python3
import argparse
import json
import os
import sys

# Ensure the backend package is importable when executed as a script
sys.path = [os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."), *sys.path]

from api.application import generate_app
from api.models import (
    db,
    NcbiMetadata,
    Marker,
    Taxonomy,
    SandpiperCache,
)
from sqlalchemy.sql import func
from sqlalchemy import distinct
# from api.duckdb_limits import register_duckdb_limits

from sandpiper.biosample_attributes import BioSampleAttributes, NcbiMetadataExtraInfos


def main(db_path: str):
    app = generate_app()
    app.config["SQLALCHEMY_DATABASE_URI"] = f"duckdb:///{db_path}"
    db.init_app(app)
    with app.app_context():
        #register_duckdb_limits(db.engine)
        db.create_all()
        SandpiperCache.query.delete()

        stats = {
            'sandpiper_total_terrabases': db.session.query(func.sum(NcbiMetadata.bases)).scalar() / 10**12,
            'sandpiper_num_runs': db.session.query(func.count(distinct(NcbiMetadata.acc))).scalar(),
            'sandpiper_num_bioprojects': db.session.query(func.count(distinct(NcbiMetadata.bioproject))).scalar(),
        }
        tax_map = {t.id: t.full_name for t in Taxonomy.query.all()}
        marker_map = {m.id: m.marker for m in Marker.query.all()}
        biosample_attrs = BioSampleAttributes(app.logger).attributes
        ncbi_infos = NcbiMetadataExtraInfos().extra_info

        db.session.add(SandpiperCache(key='stats', value=json.dumps(stats)))
        db.session.add(
            SandpiperCache(
                key='taxonomy_id_to_full_name',
                value=json.dumps(tax_map),
            )
        )
        db.session.add(
            SandpiperCache(
                key='marker_id_to_name', value=json.dumps(marker_map)
            )
        )
        db.session.add(
            SandpiperCache(
                key='biosample_attribute_definitions',
                value=json.dumps({k: v.__dict__ for k, v in biosample_attrs.items()}),
            )
        )
        db.session.add(
            SandpiperCache(
                key='ncbi_metadata_infos',
                value=json.dumps({k: v.__dict__ for k, v in ncbi_infos.items()}),
            )
        )
        db.session.commit()


def parse_args():
    parser = argparse.ArgumentParser(description="Precompute and store API caches")
    parser.add_argument("db_path", help="Path to DuckDB database file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args.db_path)
