
def get_mock_lon_item():
    address = {
        "line-1": "123 Fake Street",
        "line-2": "Test Town",
        "line-3": "Up",
        "line-4": "Line 4",
        "postcode": "12H 2ND",
        "country": "United Kingdom"
    }

    structure_position_and_dimension = {
        "height": "Unlimited height",
        "extent-covered": "All of the extent"
    }

    return {
        "geometry": {
            "type": "Point",
            "coordinates": [7, 8]
        },
        "registration-date": "2017-03-03",
        "local-land-charge": 4,
        "charge-type": "Light obstruction notice",
        "statutory-provision": "Rights of Light Act 1959 section 2(4)",
        "further-information-location": "Council Offices, Water Dept.",
        "further-information-reference": "XR12433",
        "originating-authority": "Place City Council",
        "instrument": "Certificate",
        "start-date": "2015-01-01",
        "applicant-name": "Dennis Reynolds",
        "applicant-address": address,
        "charge-address": {
            "line-1": "123 Fake Street",
            "line-2": "Test Town",
            "line-3": "Up",
            "postcode": "12H 2ND"
        },
        "charge-geographic-description": "",
        "structure-position-and-dimension": structure_position_and_dimension,
        "servient-land-interest-description": "Owner",
        "documents_filed": {
            "form-a": [{
                "bucket": "lon",
                "file_id": "form_a_id",
                "reference": "lon/form_a_id?subdirectories=test_sub_directory",
                "subdirectory": "test_sub_directory"
            }]
        }
    }
