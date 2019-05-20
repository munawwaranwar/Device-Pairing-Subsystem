"""
DPS Database Script Module
Copyright (c) 2018 Qualcomm Technologies, Inc.
 All rights reserved.
 Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
 limitations in the disclaimer below) provided that the following conditions are met:
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
 disclaimer.
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
 disclaimer in the documentation and/or other materials provided with the distribution.
 * Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
 products derived from this software without specific prior written permission.
 NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
 THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
 TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.
"""
import sys  # pragma: no cover
from flask_script import Command  # pylint: disable=deprecated-module  # pragma: no cover
from sqlalchemy.exc import SQLAlchemyError  # pragma: no cover
from app.db.indexer import Indexer  # pragma: no cover
from app.db.views import Views  # pragma: no cover


class CreateDatabase(Command):     # pragma: no cover
    """Class to manage database post creation operations."""

    def __init__(self, db):
        """Constructor"""
        super().__init__()
        self.db = db

    def _create_views(self):
        """Method to auto create views and materialized views on database."""
        db_views = Views(self.db)
        try:
            db_views.create_view()
        except SQLAlchemyError as e:
            sys.exit(1)

    def _create_indexes(self):
        """Method to perform database indexing."""
        db_indexer = Indexer(self.db)

        with self.db.engine.connect() as conn:
            with conn.execution_options(isolation_level='AUTOCOMMIT'):
                try:
                    db_indexer.create_indexes()
                except SQLAlchemyError as e:
                    sys.exit(1)

    def run(self):
        self._create_views()
        self._create_indexes()
