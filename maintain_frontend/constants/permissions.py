class Permissions(object):
    """Defines the permissions set."""
    account_management = 'Account Management'
    browse_llc = 'Browse LLC'
    retrieve_llc = 'Retrieve LLC'
    add_llc = 'Add LLC'
    vary_llc = 'Vary LLC'
    cancel_llc = 'Cancel LLC'
    request_llc1 = 'Request LLC1'
    add_lon = 'Add LON'
    vary_lon = 'Vary LON'
    cancel_lon = 'Cancel LON'
    view_report = 'View Report'
    manage_source_information = 'Manage Source Information'
    view_source_information = 'View Source Information'
    add_extent_anywhere = 'Add Extent Anywhere'
    add_extent_england = 'Add Extent England'
    add_uncommon_charges_category = 'Add Uncommon Charges Category'

    create_lr_admin = 'Create LR Admin'
    create_lr_user = 'Create LR User'
    create_la_admin = 'Create LA Admin'
    create_la_user = 'Create LA User'
    create_ooa_admin = 'Create OOA Admin'
    create_ooa_user = 'Create OOA User'

    @staticmethod
    def get_user_permissions(user_permissions):
        permission_flags = {}
        permissions = [attr for attr in dir(Permissions)
                       if not callable(getattr(Permissions, attr)) and not attr.startswith("__")]

        for key in permissions:
            permission = getattr(Permissions, key)
            permission_flags[key] = permission in user_permissions

        return permission_flags
