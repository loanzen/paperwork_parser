# Paperwork Parser

## Intro

paperwork_parser is utility for extracting data from various official documents. It uses [PDFQuery](https://github.com/jcushman/pdfquery) behind the scenes.

Currently, there is out-of-the-box support for parsing **Indian Government ITR-V PDF documents.**

The library also supports parsing of arbitrary PDF documents by allowing you to specify a 'schema' for the document. The library allows for multiple 'variants' of a document. For example, The Indian ITR-V document has slightly different fields and layout depending on whether it was generated in 2013, 2014, 2015 etc.

Check out the examples below.

This is a **work in progress**.

## Usage

### ITR-V Docs

```python

from paperwork_parser.itr.itr import ITRVDocument

doc = ITRVDocument('/path/to/itrv.pdf')

# Will load the file and perform extraction of all fields and store results
# internally.
doc.extract()

# Extracted fields are available in the `data` dict
company_name = doc.data['company_name']
gross_total_income = doc.data['gross_total_income']

```


### Configuring for custom PDF documents

Define one or more 'schemas' that inherit from `DocSchema` to go with each variant of the doc. Then define a class that inherits from `Document` and override `detect_variant()`.

```python

from paperwork_parser.base import DocField, Document

class Variant1(DocSchema):
    name = DocField((100, 30, 400, 55.5))
    address = DocField((150, 90, 650, 45))


class Variant2(DocSchema):
    name = DocField((70, 40, 350, 50))
    address = DocField((150, 120, 650, 60))
    pan_no = DocField((150, 160, 650, 125))


class MyForm(Document):

  variants = [Variant1, Variant2]

  def detect_variant(self):
      # Some calculation that returns one of the variants


def main():
    doc = MyForm('/path/to/form.pdf')
    doc.extract()
    print doc.data
```


# TODO

- Handle error cases
- Hanle data-type specification
- Handle fields being mandatory/non-mandatory.
- `Document.variants` isn't really used. `Document.detect_variant()` seems to do all the necessary work. Re-evaluate.
