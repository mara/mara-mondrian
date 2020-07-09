"""Saiku and Mondrian configuration"""

def mondrian_server_internal_url():
    """The url where to reach the mondrian server on the internal network from Mara"""
    return 'http://127.0.0.1:8080'


def mondrian_server_external_url():
    """The url under which end users can reach Saiku"""
    return 'http://127.0.0.1:8080'

