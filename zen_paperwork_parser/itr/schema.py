import re

from zen_document_parser.base import DocField, DocVariant
from zen_document_parser.exceptions import FieldParseError


class ITRVBase(DocVariant):

    # Overridden in subclasses
    for_year = None

    test_fields = ['form_title', 'assessment_year']

    form_title = DocField((52, 745, 478, 774))

    # For assessment year, grabbing a bigger box that includes labels. That way
    # we can keep the same bbox across variants, since it keeps getting
    # displaced in different years. TODO: Verify if necessary
    assessment_year = DocField((488.6, 710, 585.2, 774.1))

    company_name = DocField((72, 663, 432, 693))
    company_pan = DocField((445, 668, 578, 690))
    flat_door_block = DocField((63.7, 621.5, 234, 646.7))
    premises_building_village = DocField((235.3, 622.7, 435, 647.5))
    road_street_post_office = DocField((63.7, 578, 234, 605.5))
    area_locality = DocField((235.3, 578, 379, 605.5))
    town_city_district = DocField((63.7, 533, 234, 561.3))
    state = DocField((235.3, 533, 379, 561.3))
    pin = DocField((379, 533, 433, 561.3))

    orignal_or_revised = DocField((516, 504, 579, 520))
    designation_of_ao = DocField((216.5, 505, 432.5, 524))
    e_filing_ack_num = DocField((237.5, 484.8, 403.8, 502.8))

    gross_total_income = DocField((463, 466.2, 583.7, 483))
    deductions_under_chapter_vi_a = DocField((463, 448.1, 583.7, 466.2))
    total_income = DocField((463, 431, 583.7, 448.1))
    current_year_loss = DocField((463, 412.2, 583.7, 431))
    net_tax_payable = DocField((463, 393.4, 583.7, 412.2))
    interest_payable = DocField((463, 374.7, 583.7, 393.4))
    total_tax_and_interest_payable = DocField((463, 361, 583.7, 374.7))

    taxes_paid_advance_tax = DocField((338.5, 344.7, 446, 361))
    taxes_paid_tds = DocField((338.5, 329, 446, 344.7))
    taxes_paid_tcs = DocField((338.5, 311.7, 446, 329))
    taxes_paid_self_assessment = DocField((338.5, 294.5, 446, 311.7))
    taxes_paid_total_taxes_paid = DocField((468, 279.5, 585.2, 294.5))

    tax_payable = DocField((468, 261.5, 585.2, 279.5))
    refund = DocField((468, 246.5, 585.2, 261.5))

    def check_for_match(self):
        # TODO: Move this text out of here
        form_title_text = 'INDIAN INCOME TAX RETURN ACKNOWLEDGEMENT'
        title_match = (self.form_title == form_title_text)

        year = self._parse_assessment_year()
        year_match = (year == self.for_year)

        return all([title_match, year_match])

    def _parse_assessment_year(self):
        pattern = r'Assessment\s*Year\s*(\d\d\d\d\-\d\d)'
        year_text = self.assessment_year
        match = re.match(pattern, year_text)
        if match is None:
            raise FieldParseError(
                "Could not parse assessment year from the document."
            )

        year = match.groups()[0]  # eg. 2014-15
        year = int(year.split('-')[0])  # eg. 2014

        return year


class ITRV2013(ITRVBase):

    for_year = 2013

    form_title = DocField((52, 754, 478, 776))

    company_name = DocField((72, 667, 432, 696))
    flat_door_block = DocField((63.7, 619, 234, 650))
    premises_building_village = DocField((235.3, 619, 435, 650))
    road_street_post_office = DocField((63.7, 577, 234, 605.5))
    area_locality = DocField((235.3, 578, 379, 605.5))

    town_city_district = DocField((63.7, 533, 234, 561.3))
    state = DocField((235.3, 533, 379, 561.3))
    pin = DocField((379, 533, 433, 561.3))

    signed_by_name = DocField((185, 206, 371, 227))
    signed_by_capacity_of = DocField((444, 206, 531, 227))
    signed_by_pan = DocField((35, 183, 99, 203))
    signed_by_ip_address = DocField((167, 183, 236, 203))
    signed_by_date = DocField((256, 183, 311, 203))
    signed_by_place = DocField((328, 183, 418, 203))

    dsc_si_no_and_issuer = DocField((108.5, 146, 577, 181.5))


class ITRV2014(ITRVBase):

    for_year = 2014

    signed_by_name = DocField((185, 206, 392, 227))
    signed_by_capacity_of = DocField((469.7, 206, 575.5, 227))
    signed_by_pan = DocField((90, 183, 157, 203))
    signed_by_ip_address = DocField((226, 183, 293, 203))
    signed_by_date = DocField((313.2, 183, 370, 203))
    signed_by_place = DocField((388, 183, 481.8, 203))

    dsc_si_no_and_issuer = DocField((108.5, 146, 577, 181.5))


class ITRV2015(ITRVBase):

    for_year = 2015

    status = DocField((468, 577, 584.5, 604.7))
    aadhar_number = DocField((513.5, 532, 584.5, 560.5))

    exempt_income_agriculture = DocField((338.5, 232, 446, 245.8))
    exempt_income_others = DocField((338.5, 218.5, 446, 232))

    signed_by_name = DocField((185, 181.3, 392, 201.6))
    signed_by_capacity_of = DocField((468, 183, 575.5, 203.1))
    signed_by_pan = DocField((89, 159.6, 157, 178.4))
    signed_by_ip_address = DocField((224.8, 158, 293, 178.3))
    signed_by_date = DocField((310.2, 159.6, 369, 178.4))
    signed_by_place = DocField((386.5, 159.6, 480, 178.4))

    dsc_si_no_and_issuer = DocField((108.5, 120, 576, 154.3))
