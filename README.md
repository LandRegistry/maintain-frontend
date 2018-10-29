# Maintain Frontend

This is the frontend repository for the Maintain LLC application. This application allows you to search for local land charges based upon a location.

### Unit tests

To run the unit tests if you are using the common dev-env use the following command:
```
docker-compose exec maintain-frontend make unittest
or (using the alias)
unit-test maintain-frontend
```

### Javascript unit test with jasmine and karma runner

To setup jasmine and karma install the following packages
```
pip3 install jasmine
pip3 install nodejs
```

Install all JavaScript dependencies listed in the package.json file.
```
npm install
```

alternatively, when using the LR development environment, run from inside the docker container:
```
docker-compose exec maintain-frontend make unittest-js
```

### Run from command line
```
karma start --single-run
```

### Run in IntelliJ
add karma plugin to intellij.
Change browser config in karma.config.js to Chrome.
Setup configuration to karma.config.js.
On first run you will be prompted to install the intellij chrome plugin

### StandardJS linting
To run linting on any Javascript code, simply call `standard` from the command line.
Standard also allows you to automatically fix some linting errors by calling `standard --fix`
Alternatively, you can specify a file or directory to check by providing it as an argument eg. `standard \home\folder\*.js`

# Validation
**The master copy for form validation error message handling is in the login-frontend repository.**
**Updates made in this repository should be reflected there.**

Validation errors are generated using the following modules:

- A ValidationError class:
    - summary_message: The message to be displayed at the top of the page (error message link text).
    - inline_message: The message displayed just above the input field.

- A ValidationErrorBuilder class:
    - errors: An OrderedDict of ValidationError objects.
    - summary_heading_text: The message to be displayed at the top of the error message box.

- A FieldValidator class:
    - Takes the data to be validated, along with the name of the field and various messages to display.
    - Add each validation function to this class (e.g. is_required). The validation check should be performed by a common validator class and an error message added if the check fails.

- A CommonValidator class:
    - Contains a number of static methods to perform validation checks and return True or False.

- A "validator" class for each page that calls the FieldValidator.
    - Contains a static method "validate" which takes the fields to be validated as input, creates a new instance of ValidatorErrorBuilder, calls the FieldValidator to build the error messages, and returns the ValidationErrorBuilder instance (called validation_errors).

- A validation html partial:
    - Constructs the error message summary at the html page that contains errors.
    - Expects a variable `validation_errors` with the ValidationError dict, and `validation_summary_heading` with the heading message to be displayed.

- Checks surrounding the html input fields, with the id of the label above the input matching the input's name property. E.g.:

    *Replace input_name and input_type with the name and type of the input.*

    ```
    <div class="form-group {% if validation_errors and validation_errors['input_name'] %} error {% endif %}">
        <label id="input_name" class="form-label" for="input_name">Input name</label>
        {% if validation_errors and validation_errors['input_name'] %}
            <span class="error-message" id="error-message-input_name">{{ validation_errors['input_name'].inline_message }}</span>
        {% endif %}
        <input class="form-control" id="input_name-input" name="input_name" type="input_type" value="">
    </div>
    ```

# Naming

For reasons of compliance, the actual name of this module is maintain-frontend-ui, the "actual_name" file will cause the RPM to built with this name and it's also the name the service will run under and the folder it will be in when deployed to a server.

