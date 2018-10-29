from maintain_frontend.dependencies.country_register.country_register_data import country_register


def get_sorted_countries():
    country_list = []
    for country_code in country_register:
        if "end-date" not in country_register[country_code]["item"][0]:
            # Do not include countries that no longer exist e.g. USSR
            country_list.append(country_register[country_code]["item"][0]["name"])

    return sorted(country_list)
