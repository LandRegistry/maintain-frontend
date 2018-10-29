from marshmallow import fields, Schema, post_load, pre_load, post_dump
from namedlist import namedlist
import json


class ChargeBaseSchema(Schema):
    """Base schema class to auto (de)hyphen the field names."""
    @pre_load
    def preload_process(self, data):
        return {
            key.replace('-', '_'): value for key, value in data.items()
        }

    @post_dump
    def postdump_process(self, data):
        return {
            key.replace('_', '-'): value for key, value in data.items()
            if value
        }


class LocalLandChargeItemSchema(ChargeBaseSchema):
    """Local Land Charge schema object."""
    geometry = fields.Dict()
    local_land_charge = fields.Int()
    registration_date = fields.Date()
    originating_authority_charge_identifier = fields.Str()
    charge_type = fields.Str()
    charge_sub_category = fields.Str()
    charge_geographic_description = fields.Str()
    charge_address = fields.Dict()
    charge_creation_date = fields.Date()
    instrument = fields.Str()
    statutory_provision = fields.Str()
    further_information_location = fields.Str()
    further_information_reference = fields.Str()
    land_works_particulars = fields.Str()
    land_capacity_description = fields.Str()
    land_compensation_paid = fields.Str()
    land_compensation_amount_type = fields.Str()
    land_sold_description = fields.Str()
    unique_property_reference_numbers = fields.List(fields.Int())
    old_register_part = fields.Str()
    originating_authority = fields.Str()
    migrating_authority = fields.Str()
    migration_supplier = fields.Str()
    expiry_date = fields.Date()
    amount_originally_secured = fields.Str()
    rate_of_interest = fields.Str()
    end_date = fields.Date()
    start_date = fields.Date()
    author = fields.Dict()
    supplementary_information = fields.Str()
    schema_version = fields.Str()
    amount_of_compensation = fields.Str()

    # Create LLC object
    @post_load
    def make_charge(self, data):
        return LocalLandChargeItem(**data)


class LightObstructionNoticeItemSchema(ChargeBaseSchema):
    """Light Obstruction Notice schema object."""
    geometry = fields.Dict()
    local_land_charge = fields.Int()
    registration_date = fields.Date()
    originating_authority_charge_identifier = fields.Str()
    charge_type = fields.Str()
    charge_geographic_description = fields.Str()
    charge_address = fields.Dict()
    charge_creation_date = fields.Date()
    instrument = fields.Str()
    statutory_provision = fields.Str()
    further_information_location = fields.Str()
    further_information_reference = fields.Str()
    land_works_particulars = fields.Str()
    land_capacity_description = fields.Str()
    land_compensation_paid = fields.Str()
    land_compensation_amount_type = fields.Str()
    unique_property_reference_numbers = fields.List(fields.Int())
    old_register_part = fields.Str()
    migrating_authority = fields.Str()
    migration_supplier = fields.Str()
    expiry_date = fields.Date()
    amount_originally_secured = fields.Str()
    rate_of_interest = fields.Str()
    end_date = fields.Date()
    start_date = fields.Date()
    author = fields.Dict()
    applicant_name = fields.Str()
    applicant_address = fields.Dict()
    servient_land_interest_description = fields.Str()
    structure_position_and_dimension = fields.Dict()
    documents_filed = fields.Dict()
    tribunal_definitive_certificate_date = fields.Date()
    tribunal_temporary_certificate_date = fields.Date()
    tribunal_temporary_certificate_expiry_date = fields.Date()
    schema_version = fields.Str()

    # Create LON object
    @post_load
    def make_lon_charge(self, data):
        return LightObstructionNoticeItem(**data)


class LocalLandChargeHistoryItemSchema(ChargeBaseSchema):
    """History Entry object."""
    author = fields.Dict()
    entry_timestamp = fields.DateTime()
    item_changes = fields.Dict()
    cancelled = fields.Bool()

    # Create LLC History object
    @post_load
    def make_charge_history(self, data):
        return LocalLandChargeHistoryItem(**data)


class LLC1SearchSchema(ChargeBaseSchema):
    """LLC1 Search Parameters object."""
    location = fields.Str()
    map_coordinates = fields.Dict()
    extent = fields.Dict()
    description = fields.Str()
    llc1_url = fields.Str()

    @post_load
    def make_search(self, data):
        return LLC1Search(**data)


class PaymentLinkSchema(ChargeBaseSchema):
    """Send payment link object."""
    email = fields.Str()

    @post_load
    def make_payment_link(self, data):
        return PaymentLink(**data)


class PaymentInfoSchema(ChargeBaseSchema):
    """Payment info object."""
    payment_method = fields.Str()
    payment_ref = fields.Str()
    no_payment_notes = fields.Str()

    @post_load
    def make_payment_info(self, data):
        return PaymentInfo(**data)


class SearchDetailsSchema (ChargeBaseSchema):
    """Search reference object."""
    search_reference = fields.Str()
    search_date = fields.DateTime()
    search_lapsed = fields.Bool()
    parent_lapsed = fields.Bool()
    area_description = fields.Str()
    pdf_link = fields.Str()

    @post_load
    def make_search_details(self, data):
        return SearchDetails(**data)


class Category(object):
    name = ""
    display_name = ""
    sub_categories = []
    statutory_provisions = []
    instruments = []
    parent = None

    def __init__(self, name, display_name, sub_categories, statutory_provisions, instruments, parent):
        self.name = name
        self.display_name = display_name
        self.sub_categories = sub_categories
        self.statutory_provisions = statutory_provisions
        self.instruments = instruments
        self.parent = parent

    def to_json(self):
        subs = []
        for sub_category in self.sub_categories:
            subs.append(sub_category.to_json())

        return {
            "name": self.name,
            "display_name": self.display_name,
            "sub_categories": subs,
            "statutory_provisions": self.statutory_provisions,
            "instruments": self.instruments,
            "parent": self.parent
        }

    @staticmethod
    def from_dict(json_obj):
        subs = []
        for sub_category in json_obj['sub_categories']:
            subs.append(SubCategory.from_dict(sub_category))

        category = Category(
            json_obj['name'],
            json_obj['display_name'],
            subs,
            json_obj['statutory_provisions'],
            json_obj['instruments'],
            json_obj['parent']
        )
        return category


class SubCategory(object):
    name = ""
    display_name = ""

    def __init__(self, name, display_name):
        self.name = name
        self.display_name = display_name

    def to_json(self):
        return {
            "name": self.name,
            "display_name": self.display_name
        }

    @staticmethod
    def from_dict(json_obj):
        sub_cat = SubCategory(json_obj['name'], json_obj['display_name'])
        return sub_cat


def jsonnamedlist(schema, name, fields, **kwargs):
    """Modified namedlist to support to_json and from_json."""

    def to_json(self):
        return schema.dump(self).data

    def from_json(json_dict):
        return schema.load(json_dict).data

    def format_date_for_display(self, key):
        date = getattr(self, key)
        if date:
            return date.strftime('%-d %B %Y')
        if key == 'expiry_date':
            return 'Does not expire'
        return 'Not provided'

    def format_field_for_display(self, field):
        field = getattr(self, field)
        if field:
            return field
        return 'Not provided'

    def format_height_pos_for_display(self, key):
        pos_dim = getattr(self, 'structure_position_and_dimension')
        if isinstance(pos_dim, str):
            pos_dim = json.loads(pos_dim)

        if pos_dim:
            if key == 'height':
                if 'units' in pos_dim and pos_dim['units'] and 'height' in pos_dim and pos_dim['height']:
                    return '{} {}'.format(pos_dim['height'], pos_dim['units'])
                elif 'height' in pos_dim and pos_dim['height']:
                    return pos_dim['height']
            elif key == 'position':
                if 'part-explanatory-text' in pos_dim and pos_dim['part-explanatory-text']:
                    return pos_dim['part-explanatory-text']
                elif 'extent-covered' in pos_dim and pos_dim['extent-covered']:
                    return pos_dim['extent-covered']

        return 'Not provided'

    def format_address_for_display(self, field):
        field = getattr(self, field)
        if isinstance(field, str):
            field = json.loads(field)
        if field:
            address = []
            if 'line-1' in field and field['line-1']:
                address.append(field['line-1'])
            if 'line-2' in field and field['line-2']:
                address.append(field['line-2'])
            if 'line-3' in field and field['line-3']:
                address.append(field['line-3'])
            if 'line-4' in field and field['line-4']:
                address.append(field['line-4'])
            if 'line-5' in field and field['line-5']:
                address.append(field['line-5'])
            if 'line-6' in field and field['line-6']:
                address.append(field['line-6'])
            if 'postcode' in field and field['postcode']:
                address.append(field['postcode'])
            if 'country' in field and field['country']:
                address.append(field['country'])

            return address

        return 'Not provided'

    def format_charge_address_for_display(self, field):
        field = getattr(self, field)
        if isinstance(field, str):
            field = json.loads(field)
        if field:
            address = []
            if 'line-1' in field and field['line-1']:
                address.append(field['line-1'])
            if 'line-2' in field and field['line-2']:
                address.append(field['line-2'])
            if 'line-3' in field and field['line-3']:
                address.append(field['line-3'])
            if 'line-4' in field and field['line-4']:
                address.append(field['line-4'])
            if 'line-5' in field and field['line-5']:
                address.append(field['line-5'])
            if 'line-6' in field and field['line-6']:
                address.append(field['line-6'])
            if 'postcode' in field and field['postcode']:
                address.append(field['postcode'])

            return address

        return 'Not provided'

    obj = namedlist(name, fields, **kwargs)
    obj.to_json = to_json
    obj.from_json = from_json
    obj.format_date_for_display = format_date_for_display
    obj.format_field_for_display = format_field_for_display
    obj.format_height_pos_for_display = format_height_pos_for_display
    obj.format_address_for_display = format_address_for_display
    obj.format_charge_address_for_display = format_charge_address_for_display
    obj.schema = schema
    return obj


# Actual item object, generated via namedlist because a huge verbose class is huge and verbose
LocalLandChargeItem = jsonnamedlist(
    LocalLandChargeItemSchema(strict=True),
    "LocalLandChargeItem",
    "geometry, local_land_charge, registration_date, originating_authority_charge_identifier, charge_type, \
    charge_sub_category, charge_geographic_description, charge_address, charge_creation_date, instrument, \
    statutory_provision, further_information_location, further_information_reference, land_works_particulars, \
    land_capacity_description, land_compensation_paid, land_compensation_amount_type, land_sold_description, \
    unique_property_reference_numbers, old_register_part, originating_authority, migrating_authority, \
    migration_supplier, expiry_date, amount_originally_secured, rate_of_interest, end_date, start_date, author, \
    supplementary_information, amount_of_compensation, schema_version", default=None)

LightObstructionNoticeItem = jsonnamedlist(
    LightObstructionNoticeItemSchema(strict=True),
    "LightObstructionNoticeItem",
    "geometry, local_land_charge, registration_date, originating_authority_charge_identifier \
    charge_type, charge_geographic_description, charge_address, charge_creation_date, instrument, \
    statutory_provision, further_information_location, further_information_reference, land_works_particulars, \
    land_capacity_description, land_compensation_paid, land_compensation_amount_type, \
    unique_property_reference_numbers, old_register_part, migrating_authority, \
    migration_supplier, expiry_date, amount_originally_secured, rate_of_interest, end_date, start_date, author, \
    applicant_name, applicant_address, servient_land_interest_description, structure_position_and_dimension, \
    documents_filed, tribunal_definitive_certificate_date, tribunal_temporary_certificate_date, \
    tribunal_temporary_certificate_expiry_date, schema_version", default=None)

LocalLandChargeHistoryItem = jsonnamedlist(
    LocalLandChargeHistoryItemSchema(strict=True, many=True),
    "LocalLandChargeHistoryItem",
    "author, entry_timestamp, item_changes, cancelled", default=None)

LLC1Search = jsonnamedlist(
    LLC1SearchSchema(strict=True),
    "LLC1Search",
    "location, map_coordinates, extent, description, llc1_url, external_llc1_url",
    default=None
)

PaymentLink = jsonnamedlist(
    PaymentLinkSchema(strict=True),
    "PaymentLink",
    "email",
    default=None
)

PaymentInfo = jsonnamedlist(
    PaymentInfoSchema(strict=True),
    "PaymentInfo",
    "payment_method, payment_ref, no_payment_notes",
    default=None
)

SearchDetails = jsonnamedlist(
    SearchDetailsSchema(strict=True),
    "SearchDetails",
    "search_reference, search_date, search_lapsed, parent_lapsed, area_description, pdf_link",
    default=None
)
