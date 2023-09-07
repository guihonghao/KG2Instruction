import sys
sys.path.append('./')
import argparse
import logging
from sqlitedict import SqliteDict
from tqdm import tqdm
from src.util import LOG_FORMAT
logger = logging.getLogger(__name__)



def main(_):
    relation_db = SqliteDict(FLAGS.relation_db, flag="r")
    alias_db = SqliteDict(FLAGS.alias_db, flag="r")
    entitytype_db = SqliteDict(FLAGS.entitytype_db, autocommit=True, journal_mode='OFF')

    for qid  in tqdm(alias_db.iterkeys()):
        try:
            relations = relation_db[qid]
        except KeyError:
            continue
        else:
            types = set()
            for rel, tail_id in relations:
                if rel == "P31" or rel == "P279":
                    types.add(tail_id)
            entitytype_db[qid] = types
    logger.info('Done')
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--relation_db', type=str, default='data/db/relation.db')
    parser.add_argument('--alias_db', type=str, default='data/db/alias.db')
    parser.add_argument('--entitytype_db', type=str, default='data/db/entitytype.db')
    FLAGS, _ = parser.parse_known_args()

    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logger.info(f"{FLAGS}")

    main(_)

