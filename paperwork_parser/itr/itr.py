from paperwork_parser.base import Document
from paperwork_parser.itr.schema import ITRV2013, ITRV2014, ITRV2015


class ITRVDocument(Document):

    variants = [ITRV2013, ITRV2014, ITRV2015]
