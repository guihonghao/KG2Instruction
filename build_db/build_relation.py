import sys
sys.path.append('./')
import argparse
import logging
from sqlitedict import SqliteDict

from kglm.util import generate_from_json_bz2, load_allowed_entities, LOG_FORMAT
logger = logging.getLogger(__name__)

BAD_DATATYPES = ["Commons media file", "None", "External identifier", "URL"]


def main(_):
    allowed_entities = None
    if FLAGS.entities is not None:
        allowed_entities = load_allowed_entities(FLAGS.entities)
        print(f"Load allowed entities from {FLAGS.entities}, Length = {len(allowed_entities)}")

    db = SqliteDict(FLAGS.db, autocommit=True, journal_mode='OFF')

    for data in generate_from_json_bz2(FLAGS.input):
        iid = data['id']
        if allowed_entities is not None:
            if iid not in allowed_entities:
                continue

        claims = data['claims']
        relations = []
        for tproperty, snaks in claims.items():
            for snak in snaks:
                mainsnak = snak['mainsnak']
                if mainsnak['datatype'] in BAD_DATATYPES:
                    continue
                try:
                    value = mainsnak['datavalue']
                except KeyError:
                    continue

                if value['type'] == 'wikibase-entityid':
                    relations.append([tproperty, value['value']['id']])
                
                # Next process qualifiers
                if 'qualifiers' in snak:
                    qualifiers = snak['qualifiers']
                    for qual_prop, qual_snaks in qualifiers.items():
                        qual_prop = tproperty+':'+qual_prop
                        for qual_snak in qual_snaks:
                            # Check relation is allowed
                            if qual_snak['datatype'] in BAD_DATATYPES:
                                continue
                            try:
                                qual_value = qual_snak['datavalue']
                            except KeyError:
                                continue
                            if qual_value['type'] == 'wikibase-entityid':
                                relations.append([qual_prop, qual_value['value']['id']])
        db[iid] = relations
    logger.info('Done')
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str, help='path to wikidata dumps')
    parser.add_argument('--db', type=str, default='data/db/relation.db')
    parser.add_argument('-e', '--entities', type=str, default=None)
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logger.info(f"{FLAGS}")

    main(_)

