import inspect

from enum import IntEnum
from pdfquery import PDFQuery
from pdfminer.pdfdocument import PDFSyntaxError

from paperwork_parser.exceptions import InvalidPDFError


class DocFieldType(IntEnum):
    TEXT = 1
    NUMBER = 2
    CUSTOM = 3  # TODO: Forget this and have 'type' take a callable instead?


class DocField(object):
    def __init__(self, bbox, type=DocFieldType.TEXT, required=False,
                 description=None):
        self.bbox = bbox
        self.type = type
        self.required = required
        self.description = description


class DocSchema(object):

    @classmethod
    def as_pdf_selectors(cls, field_name=None):
        """Return pdfminer selector for specified field. If no field is
        specified, then selectors for all fields are returned.
        """
        if field_name is not None:
            field = getattr(cls, field_name, None)
            if (field is None) or (not isinstance(field, DocField)):
                raise ValueError(
                    '{field} is not a DocField attribute on {klass}'.format(
                        field=field_name, klass=cls.__name__
                    )
                )
            pdf_fields = [('assessment_year', field)]
        else:
            pdf_fields = cls.as_field_list()

        selectors = [('with_formatter', 'text')]
        for key, field in pdf_fields:
            str_coords = ', '.join(str(coord) for coord in field.bbox)
            rule = 'LTTextLineHorizontal:in_bbox("{bbox}")'.format(
                bbox=str_coords
            )
            selector = (key, rule)
            selectors.append(selector)

        return selectors

    @classmethod
    def as_field_list(cls):
        return inspect.getmembers(cls, lambda f: isinstance(f, DocField))


class Document(object):

    variants = []

    def __init__(self, file):
        """

        Args:
            file (str, File): A path to a PDF file, or a file-like object that
                represents a pdf document.

        Raises:
            IOError: If a file path is specified and the file is not found.
            InvalidPDFError: If the specified file is not a PDF.
        """
        self._data = {}

        try:
            self._file = PDFQuery(file)
        except PDFSyntaxError:
            raise InvalidPDFError("The provided file doesn't seem to be a valid PDF document")  # noqa

        self._check_configuration()

    @property
    def data(self):
        """Read only property that is loaded with document data once
        `extract()` is called.
        """
        return self._data

    def detect_variant(self):
        raise NotImplementedError(
            'Subclass Document and override this method to return a DocSchema '
            ' derived class.'
        )

    def extract(self):
        self._file.load()

        variant = self.detect_variant()

        selectors = variant.as_pdf_selectors()
        extracted = self._file.extract(selectors)

        self._data = extracted

    def _check_configuration(self):
        if not self.variants:
            raise ValueError(
                "The class '{name}' hasn't been configured with any variants."
                " Set {name}.variants to a list of DocSchema types.".format(
                    name=self.__class__.__name__
                )
            )
