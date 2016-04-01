# Zen Document Parser

## Intro

zen_document_parser is a utility for extracting data from various official documents. It uses [PDFQuery](https://github.com/jcushman/pdfquery) behind the scenes.

Currently, there is out-of-the-box support for parsing **Indian Government ITR-V PDF documents.**

The library also supports parsing of arbitrary PDF documents by allowing you to specify a 'schema' for the document. The library allows for multiple 'variants' of a document. For example, The Indian ITR-V document has slightly different fields and layout depending on whether it was generated in 2013, 2014, 2015 etc.

Check out the examples below.

This is a **work in progress**.

## Usage

### ITR-V Docs

```python

from zen_document_parser.itr.itr import ITRVDocument

# You can pass in a path or a file-like object during instantiation.
doc = ITRVDocument('/path/to/itrv.pdf')

# Will load the file, auto-detect the variant and perform extraction of all
# fields and store results internally.
doc.extract()

# Extracted fields are available in the `data` property.
print(doc.data.company_name)
print(doc.data.gross_total_income)

```


### Configuring for custom PDF documents

You basically follow these steps:

- Define one or more 'schemas', ie. `DocVariant` subclasses, to go with each variant of the doc.
- In each of these variants, define a `check_for_match()` method that returns `True` if a file was successfully parsed.
  - Make sure to define `test_fields` as an attribute on each class that is a list of all field names used inside `check_for_match()`. (This is required at present for optimization purposes, but will not be a requirement in an upcoming version.)
- Define a `Doc` subclass that represents your document. In the `variants` attribute, specify possible variants.


```python

from zen_document_parser.base import DocField, DocVariant, Document


class Variant1(DocVariant):

    # The fields that are used inside `check_for_match()`. (for optimization)
    test_fields = ['form_title']

    form_title = DocField((30, 300, 500, 380))
    name = DocField((100, 120, 400, 140.5))
    address = DocField((150, 90, 650, 110))

    def check_for_match(self):
        if self.form_title == 'Application Form For 2014':
            return True
        return False


class Variant2(DocVariant):

    test_fields = ['form_title']

    form_title = DocField((30, 290, 500, 380))
    name = DocField((70, 140, 350, 160))
    address = DocField((150, 120, 650, 140))
    pan_no = DocField((150, 80, 650, 100))

    def check_for_match(self):
        if self.form_title == 'Application Form For 2015-16':
            return True
        return False


class MyForm(Document):

    variants = [Variant1, Variant2]


def main():
    doc = MyForm('/path/to/form.pdf')
    doc.extract()
    print(doc.data.to_dict())
```


# TODO

- Hanle data-type specification
- Handle fields being mandatory/non-mandatory.
- Right now the user has to explicitly specify `test_fields` for optimization purposes. Find a way where this isn't needed.
  - Automatically load them the first time they're referred to? `extract()` can still be there as a way to bulk-load all fields in one go.
