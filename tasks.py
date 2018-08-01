

import pytest

from invoke import task
from subprocess import call

from litecoder.db import engine
from litecoder import logger, US_STATE_PATH, US_CITY_PATH
from litecoder.models import BaseModel, WOFLocality
from litecoder.sources.wof import WOFRegionRepo, WOFLocalityRepo
from litecoder.usa import USStateIndex, USCityIndex


@task
def create_db(ctx):
    """Create all tables.
    """
    BaseModel.metadata.create_all(engine)


@task
def drop_db(ctx):
    """Drop all tables.
    """
    BaseModel.metadata.drop_all(engine)


@task(drop_db, create_db)
def reset_db(ctx):
    """Drop + create tables.
    """
    pass


@task(reset_db)
def load_db(ctx):
    """Load SQLite tables.
    """
    logger.info('Loading regions.')
    WOFRegionRepo.from_env().load_db()

    logger.info('Loading localities.')
    WOFLocalityRepo.from_env().load_db()


@task
def clean_db(ctx):
    """Database post-processing.
    """
    logger.info('Cleaning localities.')
    WOFLocality.dedupe()


@task
def build_indexes(ctx):
    """Build dist indexes.
    """
    logger.info('Indexing states.')
    state_idx = USStateIndex()
    state_idx.build()
    state_idx.save(US_STATE_PATH)

    logger.info('Indexing cities.')
    city_idx = USCityIndex()
    city_idx.build()
    city_idx.save(US_CITY_PATH)


@task(build_indexes)
def test(ctx):
    """Run test suite.
    """
    call(['pytest', 'tests/test_db'])
    call(['pytest', 'tests/prod_db'])


@task(load_db, clean_db, build_indexes, test)
def build(ctx):
    """Load SQLite, build indexes, test.
    """
    pass
