import re

from paperwork_parser.base import Document
from paperwork_parser.exceptions import FieldParseError
from paperwork_parser.itr.schema import (
    ITRVSchemaCommon, ITRVSchema2013, ITRVSchema2014, ITRVSchema2015
)


class ITRVDocument(Document):

    # TODO: How are 'variants' used? Seems like detect_variant() overriding
    # takes care of everything.
    variants = [ITRVSchema2013, ITRVSchema2014, ITRVSchema2015]
    form_title_text = 'INDIAN INCOME TAX RETURN ACKNOWLEDGEMENT'

    def detect_variant(self):
        """Validate and detect which variant of ITRV document this is.

        Criteria checked are:
            1. The 'title' of the document should match 'INDIAN INCOME TAX
                RETURN ACKNOWLEDGEMENT'.
            2. The 'assessment year' should be present on the top right of the
                document and should be of the form 'Assessment Year XXXX-XX',
                where 'XXXX-XX' is a year, eg. '2014-15'. The particular
                ITRV variant is determined by the value of this year.

        Raises:
            FieldParseError: If a field that was required to detremine the
                variant could not be parsed.
        """
        selectors = ITRVSchemaCommon.as_pdf_selectors(
            'form_title', 'assessment_year'
        )
        extracted = self._file.extract(selectors)

        form_title = extracted['form_title']
        if not form_title == self.form_title_text:
            raise FieldParseError(
                'Form title did not match "{title}". Is this an ITR-V '
                'doc?'.format(title=self.form_title_text)
            )

        year_text = extracted['assessment_year']
        year = self._parse_assessment_year(year_text)

        # Variant is determined by year
        if year == 2015:
            return ITRVSchema2015
        elif year == 2014:
            return ITRVSchema2014
        elif year == 2013:
            return ITRVSchema2013
        else:
            raise ValueError('The detected year isn\'t supported')

    def _parse_assessment_year(self, year_text):
        pattern = r'Assessment\s*Year\s*(\d\d\d\d\-\d\d)'
        match = re.match(pattern, year_text)
        if match is None:
            raise FieldParseError(
                "Could not parse assessment year from the document."
            )

        year = match.groups()[0]  # eg. 2014-15
        year = int(year.split('-')[0])  # eg. 2014

        return year


"""
- 'form_title'... field is at different locations depending on variant.

"""
