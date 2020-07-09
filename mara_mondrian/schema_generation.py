import pathlib
import typing

from lxml import etree
from mara_schema.attribute import Type, Attribute
from mara_schema.data_set import DataSet
from mara_schema.metric import SimpleMetric, ComposedMetric, Aggregation
from mara_schema.sql_generation import database_identifier, table_alias_for_path



def date_dimension_xml(attribute: Attribute, name):
    """
    Return the mondrian xml fragment for a date dimension

    Requires the time.day table from https://github.com/mara/mara-etl-tools/blob/master/etl_tools/create_time_dimensions/create_tables.sql
    """
    dim = etree.Element("Dimension", name=name, type="TimeDimension", description=attribute.description,
                        foreignKey=database_identifier(name) + '_fk')
    hierarchy = etree.SubElement(dim, "Hierarchy", allMemberName=f'All {name.lower()}s', hasAll="true", name="By month")
    etree.SubElement(hierarchy, "Table", schema="time", name="day")
    etree.SubElement(hierarchy, "Level", name="Year", column="year_id", type="Integer",
                     levelType="TimeYears", uniqueMembers="true")
    etree.SubElement(hierarchy, "Level", name="Quarter", column="quarter_id", type="Integer",
                     levelType="TimeQuarters", uniqueMembers="true")
    etree.SubElement(hierarchy, "Level", name="Month", column="month_id", type="Integer",
                     levelType="TimeMonths", uniqueMembers="true")
    etree.SubElement(hierarchy, "Level", name="Day", column="day_id", type="Integer",
                     levelType="TimeDays", uniqueMembers="true")
    hierarchy = etree.SubElement(dim, "Hierarchy", allMemberName=f'All {name.lower()}s', hasAll="true", name="By week")
    etree.SubElement(hierarchy, "Table", schema="time", name="day")
    etree.SubElement(hierarchy, "Level", name="Year", column="iso_year_id", type="Integer",
                     levelType="TimeYears", uniqueMembers="true")
    etree.SubElement(hierarchy, "Level", name="Week", column="week_id", type="Integer",
                     levelType="TimeWeeks", uniqueMembers="true")
    etree.SubElement(hierarchy, "Level", name="Day", column="day_id", type="Integer",
                     levelType="TimeDays", uniqueMembers="true")
    return dim


def duration_dimension_xml(attribute: Attribute, name):
    """
    Return the mondrian xml fragment for a duration dimension

    Requires the time.duration table from https://github.com/mara/mara-etl-tools/blob/master/etl_tools/create_time_dimensions/create_tables.sql
    """

    dim = etree.Element("Dimension", name=name, type="StandardDimension", description=attribute.description,
                        foreignKey=database_identifier(name) + '_fk')
    hierarchy = etree.SubElement(dim, "Hierarchy", allMemberName=f'All {name.lower()}s', hasAll="true", name="By month")
    etree.SubElement(hierarchy, "Table", schema="time", name="duration")
    etree.SubElement(hierarchy, "Level", name="Days", column="days", type="Integer",
                     levelType="Regular", uniqueMembers="true")
    etree.SubElement(hierarchy, "Level", name="Months", column="months", type="Integer",
                     levelType="Regular", uniqueMembers="true")
    etree.SubElement(hierarchy, "Level", name="Half years", column="half_years", type="Integer",
                     levelType="Regular", uniqueMembers="true")
    etree.SubElement(hierarchy, "Level", name="Years", column="years", type="Integer",
                     levelType="Regular", uniqueMembers="true")
    hierarchy = etree.SubElement(dim, "Hierarchy", allMemberName=f'All {name.lower()}s', hasAll="true", name="By week")
    etree.SubElement(hierarchy, "Table", schema="time", name="duration")
    etree.SubElement(hierarchy, "Level", name="Days", column="days", type="Integer",
                     levelType="Regular", uniqueMembers="true")
    etree.SubElement(hierarchy, "Level", name="Weeks", column="weeks", type="Integer",
                     levelType="Regular", uniqueMembers="true")
    etree.SubElement(hierarchy, "Level", name="Four weeks", column="four_weeks", type="Integer",
                     levelType="Regular", uniqueMembers="true")
    etree.SubElement(hierarchy, "Level", name="Years", column="years", type="Integer",
                     levelType="Regular", uniqueMembers="true")
    return dim


def cube_xml(data_set: DataSet, schema_fact_table: str, table_name: str, personal_data: bool,
             high_cardinality_attributes: bool):
    cube = etree.Element("Cube", name=data_set.name, description=data_set.entity.description,
                         defaultMeasure=list(data_set.metrics.keys())[0])

    etree.SubElement(cube, "Table", schema=schema_fact_table, name=table_name)

    for path, attributes in data_set.connected_attributes(include_personal_data=personal_data).items():
        for name, attribute in attributes.items():
            if attribute.type != Type.ARRAY \
                    and (high_cardinality_attributes or
                         (not high_cardinality_attributes
                          and not attribute.high_cardinality)):
                if attribute.type == Type.DATE:
                    dim = date_dimension_xml(attribute, name)
                    cube.append(dim)
                elif attribute.type == Type.DURATION:
                    dim = duration_dimension_xml(attribute, name)
                    cube.append(dim)
                elif not path:
                    dim = etree.SubElement(cube, "Dimension", name=name, description=attribute.description)
                    hierarchy = etree.SubElement(dim, "Hierarchy", allMemberName='All ' + name, hasAll="true")
                    etree.SubElement(hierarchy, "Level", name=name, column=attribute.column_name, uniqueMembers="true")

                else:
                    entity = path[-1].target_entity
                    dim = etree.SubElement(cube, "Dimension", name=name, description=attribute.description,
                                           foreignKey=table_alias_for_path(path) + '_fk')
                    hierarchy = etree.SubElement(dim, "Hierarchy", allMemberName='All ' + name, hasAll="true",
                                                 primaryKey=entity.pk_column_name)

                    etree.SubElement(hierarchy, "Table", name=entity.table_name,
                                     schema=entity.schema_name)
                    etree.SubElement(hierarchy, "Level", name=name,
                                     column=attribute.column_name, uniqueMembers="true")

    for name, metric in data_set.metrics.items():
        if isinstance(metric, SimpleMetric):
            if metric.aggregation in [Aggregation.COUNT, Aggregation.DISTINCT_COUNT]:
                data_type = 'Integer'
            else:
                data_type = 'Numeric'
            etree.SubElement(cube, "Measure", name=name, description=metric.description,
                             column=database_identifier(metric.name), aggregator=metric.aggregation,
                             formatString=metric.number_format, datatype=data_type)

    for name, metric in data_set.metrics.items():
        if isinstance(metric, ComposedMetric):
            formula = metric.formula_template.format(
                *[f'[{metric.name}]' for metric in metric.parent_metrics]).replace('[', '[Measures].[')

            measure = etree.SubElement(cube, "CalculatedMember", name=name, dimension="Measures",
                                       description=metric.description)
            hierarchy = etree.SubElement(measure, "Formula")
            hierarchy.text = formula
            etree.SubElement(measure, "CalculatedMemberProperty", name="FORMAT_STRING",
                             value=metric.number_format)

    return cube


def write_mondrian_schema(file_name: pathlib.Path,
                          data_set_tables: typing.Dict[DataSet, typing.Tuple[str, str]],
                          personal_data: bool = False,
                          high_cardinality_attributes: bool = False):
    """Generate XML schema as a file.

    Args:
        file_name: The path of the Mondrian schema file
        data_set_tables: A dictionary with data sets as keys and tuples of strings (database schema + table) as values
            e.g. {DataSet 1: ('schema 1', 'table 1')}
        personal_data: Whether to include attributes that are marked as personal data
        high_cardinality_attributes: Whether to include attributes that are marked as have a high cardinality

    """
    root = etree.Element("Schema", name='Mondrian')

    for data_set, (fact_table_schema, table_name) in data_set_tables.items():
        root.append(cube_xml(data_set, fact_table_schema, table_name, personal_data, high_cardinality_attributes))

    tree = etree.ElementTree(root)
    tree.write(file_name.absolute().as_uri(), encoding='utf-8', pretty_print=True, xml_declaration=True)

    return True
