from paperwork_parser.base import Document
from paperwork_parser.itr.schema import (
    ITRVSchemaCommon, ITRVSchema2013, ITRVSchema2014, ITRVSchema2015
)


class ITRVDocument(Document):

    # TODO: How are 'variants' used? Seems like detect_variant() overriding
    # takes care of everything.
    variants = [ITRVSchema2013, ITRVSchema2014, ITRVSchema2015]

    def detect_variant(self):
        selectors = ITRVSchemaCommon.as_pdf_selectors('assessment_year')
        extracted = self._file.extract(selectors)

        # TODO: Move this parsing logic into cusom parser in field-definition
        year = extracted['assessment_year']
        year = int(
            year.lower().replace('assessment year', '').strip().split('-')[0]
        )

        if year == 2015:
            return ITRVSchema2015
        elif year == 2014:
            return ITRVSchema2014
        elif year == 2013:
            return ITRVSchema2013
        else:
            raise ValueError('The detected year isn\'t supported')
