import sys
import time
from typing import Optional, Dict

import lxml.etree
import requests

from . import config


def flush_mondrian_cache():
    """Reloads the mondrian schema and flushes all caches"""
    url = config.mondrian_server_internal_url() + '/flush-caches'
    try:
        if requests.get(url).status_code == 200:
            return True
    except Exception as e:
        pass

    print(f'Could not call {url}', file=sys.stderr)
    return False



def discover(request_type: str,
             restrictions: Optional[Dict] = None) -> lxml.etree._Element:
    """Creates a discover request and sends it to Mondrian Server.

    Args:
        request_type: Type of the XMLA discover request
        restrictions: Restrictions to place on the request (such as filtering by cube name)

    Returns: The body of the returned response

    """
    restrictions_xmla = "\n".join(
        [f'<{column}>{value}</{column}>' for column, value in restrictions.items()])
    xmla = f"""
    <Discover xmlns="urn:schemas-microsoft-com:xml-analysis">
        <RequestType>{request_type}</RequestType>
        <Restrictions>
            <RestrictionList>
                {restrictions_xmla}
            </RestrictionList>
        </Restrictions>
        <Properties>
           <PropertyList>
              <Catalog>dwh</Catalog>
              <DataSourceInfo>Cubes</DataSourceInfo>
              <Format>Tabular</Format>
              <Content>SchemaData</Content>
           </PropertyList>
        </Properties>
     </Discover>
     """
    return send_xmla_request(xmla)


def execute(query: str) -> lxml.etree._Element:
    """Creates an execute request and sends it to Mondrian Server.

    Args:
        query: MDX query to execute in Mondrian Server

    Returns: The body of the returned response

    """
    xmla = f"""
    <Execute xmlns="urn:schemas-microsoft-com:xml-analysis">
        <Command>
           <Statement>
              <![CDATA[{query}]]>
           </Statement>
        </Command>
        <Properties>
           <PropertyList>
              <Catalog>Mondrian</Catalog>
              <DataSourceInfo>Mondrian</DataSourceInfo>
              <Format>Multidimensional</Format>
              <Content>Data</Content>
              <AxisFormat>TupleFormat</AxisFormat>
           </PropertyList>
        </Properties>
     </Execute>"""
    return send_xmla_request(xmla)


def send_xmla_request(xmla: str, attempt: Optional[int] = 0) -> lxml.etree._Element:
    """Constructs an XMLA request and sends it to Mondrian Server including retries on failed attempts.
    Parses the

    Args:
        xmla: XMLA to be send as the body of the request
        attempt: How many times the request was already attempted

    Returns: Body of the parsed response

    """
    soap_xml = f"""<?xml version="1.0"?>
    <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
        <SOAP-ENV:Header />
        <SOAP-ENV:Body>{xmla}</SOAP-ENV:Body>
    </SOAP-ENV:Envelope>
    """
    session = requests.Session()
    session.trust_env = False
    response = session.post(f'{config.mondrian_server_internal_url()}/xmla', data=soap_xml.encode('utf-8'),
                            headers={'Content-type': 'text/xml'})

    utf8_parser = lxml.etree.XMLParser(ns_clean=True, encoding='utf-8')
    tree = lxml.etree.fromstring(response.text.encode('utf-8'), parser=utf8_parser)
    body = tree.find("SOAP-ENV:Body", namespaces=tree.nsmap)
    fault = body.find("SOAP-ENV:Fault", namespaces=tree.nsmap)
    if fault is not None:
        if attempt < 1:
            time.sleep(2)
            return send_xmla_request(xmla, attempt=(attempt + 1))
        else:
            code = fault.find('faultcode').text
            error = fault.find('faultstring').text
            description = fault.find(
                'detail'
            ).find(
                "XA:error", namespaces={"XA": "http://mondrian.sourceforge.net"}
            ).find("desc").text

            raise MondrianError(f"""{code} - {error}
            {description}""")
    else:
        return body


class MondrianError(Exception):
    pass
