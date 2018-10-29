from io import BytesIO
from unittest import TestCase
from unittest.mock import patch
from maintain_frontend.add_land_charge.validation.upload_shapefile_validator import UploadShapefileValidator

# Contents of zip file with valid shapefile containing a single point
VALID_SHAPEFILE = b"PK\x03\x04\x14\x00\x08\x00\x08\x00\xf8HuL\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f" \
                  b"\x00\x10\x00valid_point.shxUX\x0c\x00\xec \xb2Z\xe4 \xb2Z," \
                  b"*\xb9rc`P\xe7b\xc0\x0e\xcc^0300\x02\x19\t\xba/\x0e<z$\xe8x\xca\xf6\xa8\xef\x86\xeb\xdf\x1c\xd0" \
                  b"\xf98\xf4#\x03# \xe6\x02\x00PK\x07\x08\xab\x9f39+\x00\x00\x00l\x00\x00\x00PK\x03\x04\x14\x00\x08" \
                  b"\x00\x08\x00zGuL\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x10\x00valid_point" \
                  b".cpgUX\x0c\x00\xe4 \xb2Z\x08\x1f\xb2Z," \
                  b"*\xb9r\x0b\rq\xd3\xb5\x00\x00PK\x07\x08P<\x81\x0e\x07\x00\x00\x00\x05\x00\x00\x00PK\x03\x04\n" \
                  b"\x00\x00\x00\x00\x00\x01IuL\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x00\x10" \
                  b"\x00__MACOSX/UX\x0c\x00\xf1 \xb2Z\xf1 \xb2Z," \
                  b"*\xb9rPK\x03\x04\x14\x00\x08\x00\x08\x00zGuL\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a" \
                  b"\x00\x10\x00__MACOSX/._valid_point.cpgUX\x0c\x00\xe4 \xb2Z\x08\x1f\xb2Z," \
                  b"*\xb9rc`\x15cg`b`\xf0MLV\xf0\x0fV\x88P\x80\x02\x90\x18\x03'\x10\x1b\x01\xf1\x02 " \
                  b"\x06\xf1/1\x10\x05\x1cCB\x82\xa0L\x90\x8e\x15@\xac\x85\xa6\x84\x11!\xae\x92\x9c\x9f\xab\x97XP" \
                  b"\x90\x93\xaa\x97\x9bZ\x92\x98\x92X\x92h\x15\x9f\xed\xeb\xe2Y\x92\x9a\x1bZ\x9cZ\x14\x92\x98^\xcc" \
                  b"\xc0\x90T\x90\x93Y\\b`\xb0\x80\x03j\x00#\x92I\xc8\x80\x13\x00PK\x07\x08\x96\xde\x02\xa8m\x00\x00" \
                  b"\x00\xd2\x00\x00\x00PK\x03\x04\x14\x00\x08\x00\x08\x00\xf8HuL\x00\x00\x00\x00\x00\x00\x00\x00" \
                  b"\x00\x00\x00\x00\x0f\x00\x10\x00valid_point.shpUX\x0c\x00\xec \xb2Z\xe4 \xb2Z," \
                  b"*\xb9rc`P\xe7b\xc0\x0e\x1c^0300\x02\x19\t\xba/\x0e<z$\xe8x\xca\xf6\xa8\xef\x86\xeb\xdf\x1c\xd0" \
                  b"\xf98\xf4#\x03\x901\\\xd8\xcc\x02\x00PK\x07\x08\x81\xe9\r\x89-\x00\x00\x00\x80\x00\x00\x00PK\x03" \
                  b"\x04\x14\x00\x08\x00\x08\x00\xf8HuL\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x10" \
                  b"\x00valid_point.dbfUX\x0c\x00\xec \xb2Z\xe4 \xb2Z," \
                  b"*\xb9rc\x8eg\x97bd``pd\xe0f\xc0\x062S\xe0L?\x10\xc1\x85&\xcf\xab\xa0\x05\x07R\x00PK\x07\x08\x1aj" \
                  b"=L\x1e\x00\x00\x00M\x00\x00\x00PK\x03\x04\x14\x00\x08\x00\x08\x00zGuL\x00\x00\x00\x00\x00\x00" \
                  b"\x00\x00\x00\x00\x00\x00\x0f\x00\x10\x00valid_point.prjUX\x0c\x00\xe4 \xb2Z\x08\x1f\xb2Z," \
                  b"*\xb9rm\xcfQk\x830\x10\x07\xf0\xaf2\xf2\x9c\x16c4.\x8f\xb6\x8a\xb3`-\xd6>\x89\x84`\xafm\xc0F\x88" \
                  b"\xd9\xc6\xbe\xfd\xcen\x0c\n\xcbC\x08\xc7/w\xf7?4\xf5n{\xecH}," \
                  b"6\x8aI.\xd4\xc6\x19o\xe6\x9b\xdako&\xabGU8s&\xb4\xc8\xebb\x81x\xa9\x05\xbf,\x98\xd0," \
                  b"mOUG2\xf5\xd7\x80\xd0\xe3\xe1-o\xea2\xebHj\xdc\x97b\xaf< T\xf0$\x89\x05_s)h(" \
                  b"\xe5\x9a\x87\x91\x14\x91\xe8{zh\xca*\xc7\x1e\x85\x03\xb0\x9ff\xb8\x11\x1a\xf4\xf4\xb4/[" \
                  b"\xec\x0bW\xacba\x1d\xb0$\x8ay(" \
                  b"\xc3\x98I\x19\xe1#~|\xadw\xf9\xb6-\xeb}GZ\xa7\xed\xfc\x01n\x06U\x81\x1b\xb4\x9f\x1cA\x916i\x95" \
                  b"\xb7y\xd3\x91\x11\x03\xf9\xf73\xa8\xe9\xa2&g\xae\xc6\x12\x1a\xc9'2\x80\xf5\x0e#\xdf\x013\x1b\x8d" \
                  b"`\x15>\x81y\xd0#\xa8\x8b\x1e\x96\xee\xb8\x95\x94R\x04," \
                  b"LX\xf2\xc4.z\xc45@\xcf\xde\xd8+N\t\x96\xf3\x8f\xb0\x93\xf3\xb7\x07Y\xb1_\xf3\x93\xbb\x02\x0f8" \
                  b"\x80\xf5\xfd7PK\x07\x08\xce\n\xc2\xef\x19\x01\x00\x00\xa1\x01\x00\x00PK\x03\x04\x14\x00\x08\x00" \
                  b"\x08\x00zGuL\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1a\x00\x10\x00__MACOSX" \
                  b"/._valid_point.prjUX\x0c\x00\xe4 \xb2Z\x08\x1f\xb2Z," \
                  b"*\xb9rc`\x15cg`b`\xf0MLV\xf0\x0fV\x88P\x80\x02\x90\x18\x03'\x10\x1b\x01\xf1\x02 " \
                  b"\x06\xf1/1\x10\x05\x1cCB\x82\xa0L\x90\x8e\x15@\xac\x85\xa6\x84\x11!\xae\x92\x9c\x9f\xab\x97XP" \
                  b"\x90\x93\xaa\x97\x9bZ\x92\x98\x92X\x92h\x15\x9f\xed\xeb\xe2Y\x92\x9a\x1bZ\x9cZ\x14\x92\x98^\xcc" \
                  b"\xc0\x90T\x90\x93Y\\b`\xb0\x80\x03j\x00#\x92I\xc8\x80\x13\x00PK\x07\x08\x96\xde\x02\xa8m\x00\x00" \
                  b"\x00\xd2\x00\x00\x00PK\x03\x04\x14\x00\x08\x00\x08\x00zGuL\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
                  b"\x00\x00\x00\x0f\x00\x10\x00valid_point.qpjUX\x0c\x00\xe4 \xb2Z\x08\x1f\xb2Z," \
                  b"*\xb9rm\x92\xdd\x8a\xdb0\x10\x85\xef\xfb\x14F\xd7\x8a\xab?K\xd6\xa5wW8^\x88\x1dl\x85\xb6\x98" \
                  b"`\x84\xa3$\x02\xaf\r\xb2\xdb\xd2\xb7\xaf\xd2\xec.\x84Z\x17\x03\x1a}:3:\xa3}]\xbd>7-\xa8\x9a\xfc" \
                  b")\xc2\x92\xf2\xe8k\xf4\xe4\xdd\xe2\xe6kT\x9a\xc5M\xa3\x19\xa2\xdc\xbb\x13\x80\xb9\xaa\xf2\x07" \
                  b"\x14\xc0\x97L\x1fv\xf7Lw\xcf4\xfb\xad\xaa\xab\xe2\xa5\x05\x99\xf3\x7f\"\x9cR\x04 " \
                  b"\xa7B$\x9c\xc6TrH\xa4\x8c)a\x923\x0e\xb3\x83\xdeVu\xa1\x7f\xb4@\xed\x9b\x1c@ " \
                  b"\x10\xc2\xe0x\x84\xba\xfa\x967)k\x19\xe31c)\xdc`\x92\xc48\x110a$F\x1c\xa2\xb0\t\x810\x11b\xca" \
                  b"\x08\xdc\x10\x14\xb3T\x1eW49\x11\xe2\xa6\xb9\xaf\x8b\x9d\n\xdd\xe6\xde\xda\xf1\xb7\xeb\xaf\x00" \
                  b"\xa2\x15<\x95\xf7\x16\x0ee\xa1[p\xb2\x97\x80\x072FX\xb0\x84\x12I\x12," \
                  b"%\xa3t\xe5\xaa\xc4\x84\xdc\xae\xfe\x7f\xc2>{" \
                  b"\xa8^\xd5\xb3.\xaa\xb2\x05\xda\x9bq\xfee\xfdl\xbb\x9d\xf5\xbdY&\x0f\x02\x91\xd5\xd9NiU\xb7`\x08" \
                  b"\xfe/?O\xb6\x9b\xce\xdd\xe4\xdd\xc5\x8d\x002\xf9\x80\xf4v\\\xbc\x19\xba7\x1bF\xe4L\x006\xe4\x01" \
                  b"\x98{3\xd8\xeel\xfa\x9bzx\x85\x94\x92#L\x04\x16\x0f\xd8\xd9\x0c\xa1\rk\xe6\xc5\x8d\x97P\x05\xdd" \
                  b"\xd6\n1N~\xb9\xfeC6\xf8\x9d\xb9\xfb\xf4f\x17\x1fl\xc2k\xae\xbc\xcf4\xfb^\x84\xdf\xa3>j\xa8\xac" \
                  b"\xd1\x1f\xc9\xf2S\xb6\xacj\xbd]s0\x18\x88P\x90\xf9\xf2\x17PK\x07\x08\xb8Pr\x9a\x87\x01\x00\x00" \
                  b"\xb2\x02\x00\x00PK\x03\x04\x14\x00\x08\x00\x08\x00zGuL\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
                  b"\x00\x00\x1a\x00\x10\x00__MACOSX/._valid_point.qpjUX\x0c\x00\xe4 \xb2Z\x08\x1f\xb2Z," \
                  b"*\xb9rc`\x15cg`b`\xf0MLV\xf0\x0fV\x88P\x80\x02\x90\x18\x03'\x10\x1b\x01\xf1\x02 " \
                  b"\x06\xf1/1\x10\x05\x1cCB\x82\xa0L\x90\x8e\x15@\xac\x85\xa6\x84\x11!\xae\x92\x9c\x9f\xab\x97XP" \
                  b"\x90\x93\xaa\x97\x9bZ\x92\x98\x92X\x92h\x15\x9f\xed\xeb\xe2Y\x92\x9a\x1bZ\x9cZ\x14\x92\x98^\xcc" \
                  b"\xc0\x90T\x90\x93Y\\b`\xb0\x80\x03j\x00#\x92I\xc8\x80\x13\x00PK\x07\x08\x96\xde\x02\xa8m\x00\x00" \
                  b"\x00\xd2\x00\x00\x00PK\x01\x02\x15\x03\x14\x00\x08\x00\x08\x00\xf8HuL\xab\x9f39+\x00\x00\x00l" \
                  b"\x00\x00\x00\x0f\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00@\xa4\x81\x00\x00\x00\x00valid_point" \
                  b".shxUX\x08\x00\xec \xb2Z\xe4 " \
                  b"\xb2ZPK\x01\x02\x15\x03\x14\x00\x08\x00\x08\x00zGuLP<\x81\x0e\x07\x00\x00\x00\x05\x00\x00\x00" \
                  b"\x0f\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00@\xa4\x81x\x00\x00\x00valid_point.cpgUX\x08\x00\xe4 " \
                  b"\xb2Z\x08\x1f\xb2ZPK\x01\x02\x15\x03\n\x00\x00\x00\x00\x00\x01IuL\x00\x00\x00\x00\x00\x00\x00" \
                  b"\x00\x00\x00\x00\x00\t\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00@\xfdA\xcc\x00\x00\x00__MACOSX/UX" \
                  b"\x08\x00\xf1 \xb2Z\xf1 \xb2ZPK\x01\x02\x15\x03\x14\x00\x08\x00\x08\x00zGuL\x96\xde\x02\xa8m\x00" \
                  b"\x00\x00\xd2\x00\x00\x00\x1a\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00@\xa4\x81\x03\x01\x00" \
                  b"\x00__MACOSX/._valid_point.cpgUX\x08\x00\xe4 " \
                  b"\xb2Z\x08\x1f\xb2ZPK\x01\x02\x15\x03\x14\x00\x08\x00\x08\x00\xf8HuL\x81\xe9\r\x89-\x00\x00\x00" \
                  b"\x80\x00\x00\x00\x0f\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00@\xa4\x81\xc8\x01\x00\x00valid_point" \
                  b".shpUX\x08\x00\xec \xb2Z\xe4 " \
                  b"\xb2ZPK\x01\x02\x15\x03\x14\x00\x08\x00\x08\x00\xf8HuL\x1aj=L\x1e\x00\x00\x00M\x00\x00\x00\x0f" \
                  b"\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00@\xa4\x81B\x02\x00\x00valid_point.dbfUX\x08\x00\xec " \
                  b"\xb2Z\xe4 \xb2ZPK\x01\x02\x15\x03\x14\x00\x08\x00\x08\x00zGuL\xce\n\xc2\xef\x19\x01\x00\x00\xa1" \
                  b"\x01\x00\x00\x0f\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00@\xa4\x81\xad\x02\x00\x00valid_point" \
                  b".prjUX\x08\x00\xe4 \xb2Z\x08\x1f\xb2ZPK\x01\x02\x15\x03\x14\x00\x08\x00\x08\x00zGuL\x96\xde\x02" \
                  b"\xa8m\x00\x00\x00\xd2\x00\x00\x00\x1a\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00@\xa4\x81\x13\x04" \
                  b"\x00\x00__MACOSX/._valid_point.prjUX\x08\x00\xe4 " \
                  b"\xb2Z\x08\x1f\xb2ZPK\x01\x02\x15\x03\x14\x00\x08\x00\x08\x00zGuL\xb8Pr\x9a\x87\x01\x00\x00\xb2" \
                  b"\x02\x00\x00\x0f\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00@\xa4\x81\xd8\x04\x00\x00valid_point" \
                  b".qpjUX\x08\x00\xe4 \xb2Z\x08\x1f\xb2ZPK\x01\x02\x15\x03\x14\x00\x08\x00\x08\x00zGuL\x96\xde\x02" \
                  b"\xa8m\x00\x00\x00\xd2\x00\x00\x00\x1a\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00@\xa4\x81\xac\x06" \
                  b"\x00\x00__MACOSX/._valid_point.qpjUX\x08\x00\xe4 " \
                  b"\xb2Z\x08\x1f\xb2ZPK\x05\x06\x00\x00\x00\x00\n\x00\n\x00\xf5\x02\x00\x00q\x07\x00\x00\x00\x00 "

VALIDATOR_PATH = 'maintain_frontend.add_land_charge.validation.upload_shapefile_validator'


class TestUploadShapefileValidator(TestCase):

    def test_valid_existing_geometries(self):
        shapefile = BytesIO(VALID_SHAPEFILE)

        validation_errors = UploadShapefileValidator.validate(shapefile, None, False)

        self.assertEqual(len(validation_errors.errors), 0)

    def test_valid_no_existing_geometries(self):
        geometry_session_obj = {
            'features': []
        }
        shapefile = BytesIO(VALID_SHAPEFILE)

        validation_errors = UploadShapefileValidator.validate(shapefile, geometry_session_obj, False)

        self.assertEqual(len(validation_errors.errors), 0)

    def test_upload_required(self):
        validation_errors = UploadShapefileValidator.validate(None, None, False)

        self.assertEqual(len(validation_errors.errors), 1)
        self.assertEqual(validation_errors.errors['shapefile-input'].inline_message, "Upload a file")
        self.assertEqual(validation_errors.errors['shapefile-input'].summary_message, "Upload a file")

    def test_filesize_too_big(self):
        shapefile = BytesIO(b'a' * 1000001)
        validation_errors = UploadShapefileValidator.validate(shapefile, None, False)

        self.assertEqual(len(validation_errors.errors), 1)
        self.assertEqual(validation_errors.errors['shapefile-input'].inline_message, "Upload a smaller file")
        self.assertEqual(validation_errors.errors['shapefile-input'].summary_message, "File is bigger than 1MB")

    def test_invalid_shapefile(self):
        shapefile = BytesIO()

        validation_errors = UploadShapefileValidator.validate(shapefile, None, False)

        self.assertEqual(len(validation_errors.errors), 1)
        self.assertEqual(validation_errors.errors['shapefile-input'].inline_message, "Upload a different file")
        self.assertEqual(validation_errors.errors['shapefile-input'].summary_message, "File not uploaded")

    @patch('{}.fiona.BytesCollection'.format(VALIDATOR_PATH))
    def test_shapefile_contents_required(self, bytes_collection_mock):
        mock_shape_collection = []

        shapefile = BytesIO()

        bytes_collection_mock.return_value.__enter__.return_value = mock_shape_collection
        validation_errors = UploadShapefileValidator.validate(shapefile, None, False)

        self.assertEqual(len(validation_errors.errors), 1)
        self.assertEqual(validation_errors.errors['shapefile-input'].inline_message, "Upload a different file")
        self.assertEqual(validation_errors.errors['shapefile-input'].summary_message, "File not uploaded")

    @patch('{}.fiona.BytesCollection'.format(VALIDATOR_PATH))
    def test_too_many_extents_in_shapefile(self, bytes_collection_mock):
        mock_shape_collection = []
        for i in range(0, 501):
            mock_shape_collection.append({'geometry': 'a geometry'})

        shapefile = BytesIO()

        bytes_collection_mock.return_value.__enter__.return_value = mock_shape_collection
        validation_errors = UploadShapefileValidator.validate(shapefile, None, False)

        self.assertEqual(len(validation_errors.errors), 1)
        self.assertEqual(validation_errors.errors['shapefile-input'].inline_message, "Too many extents")
        self.assertEqual(validation_errors.errors['shapefile-input'].summary_message,
                         "Number of extents must be 500 (or fewer)")

    @patch('{}.fiona.BytesCollection'.format(VALIDATOR_PATH))
    def test_too_many_extents_in_total(self, bytes_collection_mock):
        mock_shape_collection = []
        for i in range(0, 498):
            mock_shape_collection.append({'geometry': 'a geometry'})

        geometry_session_obj = {
            'features': [
                {'geometry': 'a geometry'},
                {'geometry': 'another geometry'},
                {'geometry': 'a third geometry'}
            ]
        }

        shapefile = BytesIO()

        bytes_collection_mock.return_value.__enter__.return_value = mock_shape_collection
        validation_errors = UploadShapefileValidator.validate(shapefile, geometry_session_obj, False)

        self.assertEqual(len(validation_errors.errors), 1)
        self.assertEqual(validation_errors.errors['shapefile-input'].inline_message, "Too many extents")
        self.assertEqual(validation_errors.errors['shapefile-input'].summary_message,
                         "Number of extents must be 500 (or fewer)")

    @patch('{}.fiona.BytesCollection'.format(VALIDATOR_PATH))
    def test_too_many_extents_validation_when_already_uploaded(self, bytes_collection_mock):
        mock_shape_collection = [{'geometry': 'a geometry'}, {'geometry': 'another geometry'}]

        geometry_session_obj = {
            'features': []
        }

        for i in range(0, 499):
            geometry_session_obj['features'].append({'geometry': 'some geometry'})

        shapefile = BytesIO()

        bytes_collection_mock.return_value.__enter__.return_value = mock_shape_collection
        validation_errors = UploadShapefileValidator.validate(shapefile, None, True)

        self.assertEqual(len(validation_errors.errors), 0)
        # self.assertEqual(validation_errors.errors['shapefile-input'].inline_message, "Too many extents")
        # self.assertEqual(validation_errors.errors['shapefile-input'].summary_message,
        #                  "Number of extents must be 500 (or fewer)")