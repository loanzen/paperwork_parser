from enum import IntEnum
from pdfquery import PDFQuery
from pdfminer.pdfdocument import PDFSyntaxError

from zen_document_parser.exceptions import InvalidPDFError, UnknownVariantError


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


class DocVariantMeta(type):
    """Metaclass for DocVariant. Allows defining a 'schema' based on DocFields
    on a DocVariant subclass (similar to Django models).
    """

    def __new__(cls, cls_name, bases, members):

        # To ensure proper handling of fields defined in parents
        parents = [b for b in bases if isinstance(b, DocVariantMeta)]

        module = members.pop('__module__')
        new_class = super(DocVariantMeta, cls).__new__(
            cls, cls_name, bases, {'__module__': module}
        )

        _meta = {'field_info': {}}
        setattr(new_class, '_meta', _meta)
        meta_field_info = _meta['field_info']

        misc_members = []
        doc_field_members = []

        # First get doc fields from parents
        for parent in parents:
            doc_field_members.extend(parent._meta['field_info'].iteritems())

        # Collect doc fields
        for field_name, field_obj in members.iteritems():
            if isinstance(field_obj, DocField):
                doc_field_members.append((field_name, field_obj))
            else:
                misc_members.append((field_name, field_obj))

        # Put misc stuff into class
        for member_name, member_value in misc_members:
            setattr(new_class, member_name, member_value)

        # Process doc fields
        for field_name, field_obj in doc_field_members:
            # Populate field info in meta
            meta_field_info[field_name] = field_obj

            # TODO: Fix initial value. This is a placeholder.
            setattr(new_class, field_name, field_name)

        return new_class


class DocVariant(object):

    __metaclass__ = DocVariantMeta

    # The fields that are loaded up for use inside check_for_match(). This is
    # an optimization that avoids us needing to extract every field of the
    # document just to perform a test using a few fields.
    # TODO: Find a way that doesn't require specifying this manually.
    test_fields = []

    def __init__(self, file):
        """
        Args:
            file (PDFQuery object): A **loaded** PDFQuery object that will
                be used internally to extract fields.
        """
        self._file = file

    def check_for_match(self):
        raise NotImplementedError(
            'Override this to perform some test that returns True if the file '
            'matches this variant, False otherwise. Make sure all fields '
            'used in this method are specified in the `test_fields` attribute.'
        )

    def load_test_fields_and_check_for_match(self):
        """Extracts `test_fields` and runs `check_for_match()`.

        This method allows users to not care about performing extraction
        related stuff - they'll just override `check_for_match()` and write
        check related logic.
        """
        self.extract(*self.test_fields)
        return self.check_for_match()

    def extract(self, *field_names):
        """Extracts specified fields from `self._file`. If no fields are
        specified, **all** fields are extracted.
        """
        selectors = self.as_pdf_selectors(*field_names)
        extracted = self._file.extract(selectors)
        for field, value in extracted.iteritems():
            setattr(self, field, value)

    def as_pdf_selectors(self, *field_names):
        """Return pdfminer selector for specified field. If no field is
        specified, then selectors for **all** fields are returned.
        """
        # Collate relevant fields
        if field_names:
            pdf_fields = []
            for field_name in field_names:
                field = self._meta['field_info'].get(field_name)
                if field is None:
                    raise ValueError('{field} is not a DocField defined on {klass}'.format(  # noqa
                            field=field_name, klass=self.__class__.__name__
                    ))
                pdf_fields.append((field_name, field))
        else:
            pdf_fields = self._meta['field_info'].items()

        selectors = [('with_formatter', 'text')]
        for key, field in pdf_fields:
            str_coords = ', '.join(str(coord) for coord in field.bbox)
            rule = 'LTTextLineHorizontal:in_bbox("{bbox}")'.format(
                bbox=str_coords
            )
            selector = (key, rule)
            selectors.append(selector)

        return selectors

    def to_dict(self):
        fields = self._meta['field_info']
        out = dict((fname, getattr(self, fname)) for fname in fields)
        return out


class Document(object):

    # The variants of this document. A list of DocVariant subclasses. Files
    # will be checked against these variants to find an appropriate match.
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
        self._data = None
        self._variant = None  # TODO: Is this needed?

        self._check_configuration()

        try:
            self._file = PDFQuery(file)
        except PDFSyntaxError:
            raise InvalidPDFError("The provided file doesn't seem to be a valid PDF document")  # noqa

    @property
    def data(self):
        """Read only property that is loaded with document data once
        `extract()` is called. This will be an instance of a DocVariant
        subclass.
        """
        return self._data

    def detect_variant(self):
        """Tests the loaded file against all variants specified in the
        ``variants`` attribute and returns the one that matches.

        Returns:
            One of the DocVariant subclasses specified in `self.variants`
            or None, if no suitable match is found.
        """
        variant_objs = [var(self._file) for var in self.variants]
        matched_variant = None
        for variant in variant_objs:
            if variant.load_test_fields_and_check_for_match():
                matched_variant = variant
                break
        return matched_variant

    def extract(self):
        """Loads up file, detects the variant of the document and performs
        extraction of fields. Extracted information is stored in ``self.data``.
        """
        # Load happens here (lazy)
        self._file.load()

        variant = self._variant = self.detect_variant()

        if variant is None:
            raise UnknownVariantError(
                'The specified file {file} could not be matched against any '
                'of the variants specified in `{cls_name}.variants`.\n If '
                'this is a new variant, please define an appropriate '
                'DocVariant subclass for it.'.format(
                    file=self._file.file.name, cls_name=self.__class__.__name__
                )
            )

        # Load completely
        variant.extract()

        self._data = variant

    def _check_configuration(self):
        if not self.variants:
            raise ValueError(
                "The class '{name}' hasn't been configured with any variants."
                " Set {name}.variants to a list of DocVariant types.".format(
                    name=self.__class__.__name__
                )
            )
