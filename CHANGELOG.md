# Changelog

## 2.0.2 (2020-01-24)

- Include all versioned package files in wheel (not only python files)


## 2.0.1 (2020-10-27)

- Fix broken Makefile: escape sed delimiter in substitution values (#3)


## 2.0.0 (2020-10-23)

- Update `mondrian-server.war` built with Java 11

`required changes`

The new war file is built and works with `Java 11`.
It can, also, run with `Java 8` but a careful check of the functionality is highly recommended in this case.

## 1.0.2 (2020-09-29)

- Makefile bug fix for user names with `@` in the name

## 1.0.0 - 1.0.1 (2020-07-09)

- Initial release