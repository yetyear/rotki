from http import HTTPStatus
from typing import TYPE_CHECKING, Any

import requests

from rotkehlchen.tests.utils.api import (
    api_url_for,
    assert_error_response,
    assert_proper_response_with_result,
)

if TYPE_CHECKING:
    from rotkehlchen.api.server import APIServer


def _get_all_location_mappings(rotkehlchen_api_server: 'APIServer') -> Any:
    """Utility function to return all the location asset mappings in the DB."""
    response = requests.post(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
    )
    return assert_proper_response_with_result(response=response)


def test_location_asset_mappings_query(rotkehlchen_api_server: 'APIServer') -> None:
    """Test the location asset mappings API for querying the mappings."""
    # query all the mappings
    result = _get_all_location_mappings(rotkehlchen_api_server)
    assert len(result['entries']) == result['entries_found'] == result['entries_total'] == 1500

    # query all common mappings
    response = requests.post(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={'location': None},
    )
    result = assert_proper_response_with_result(response)
    assert len(result['entries']) == result['entries_found'] == 33

    # query all common mappings
    response = requests.post(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={'location': None},
    )
    result = assert_proper_response_with_result(response)
    assert len(result['entries']) == result['entries_found'] == 33

    # query all kraken mappings
    response = requests.post(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={'location': 'kraken'},
    )
    result = assert_proper_response_with_result(response)
    assert len(result['entries']) == result['entries_found'] == 228


def test_location_asset_mappings_add(rotkehlchen_api_server: 'APIServer') -> None:
    """Test the location asset mappings API for adding the mappings."""
    all_mappings = _get_all_location_mappings(rotkehlchen_api_server)['entries']
    added_mappings = [{
        'asset': 'eip155:1/erc20:0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',
        'location_symbol': 'NEW1',
        'location': 'binance',
    }, {
        'asset': 'eip155:1/erc20:0xF57e7e7C23978C3cAEC3C3548E3D615c346e79fF',
        'location_symbol': 'NEW2',
        'location': 'kraken',
    }]

    # add two new mappings
    response = requests.put(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={
            'entries': added_mappings,
        },
    )
    result = assert_proper_response_with_result(response)
    assert result is True

    # check that the mappings were indeed added
    response = requests.post(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={
            'offset': 0,
            'limit': 2000,
        },
    )
    result = assert_proper_response_with_result(response)
    all_mappings_after_addition = result['entries']
    assert len(all_mappings_after_addition) == result['entries_found'] == 1502
    for new_mapping in added_mappings:
        assert new_mapping not in all_mappings
        assert new_mapping in all_mappings_after_addition


def test_location_asset_mappings_update(rotkehlchen_api_server: 'APIServer') -> None:
    """Test the location asset mappings API for updating the mappings."""
    all_mappings = _get_all_location_mappings(rotkehlchen_api_server)['entries']

    # updated a mapping of asset NEW1
    initial_mapping = all_mappings[0]
    updated_mapping = {
        'asset': 'eip155:1/erc20:0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
        'location_symbol': all_mappings[0]['location_symbol'],
        'location': all_mappings[0]['location'],
    }
    response = requests.patch(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={'entries': [updated_mapping]},
    )
    result = assert_proper_response_with_result(response)
    assert result is True

    # check if the mappings is updated
    all_mappings_after_update = _get_all_location_mappings(rotkehlchen_api_server)['entries']
    assert all_mappings_after_update[0] == updated_mapping
    assert initial_mapping in all_mappings and initial_mapping not in all_mappings_after_update
    assert updated_mapping not in all_mappings and updated_mapping in all_mappings_after_update


def test_location_asset_mappings_delete(rotkehlchen_api_server: 'APIServer') -> None:
    """Test the location asset mappings API for deleting the mappings."""
    all_mappings = _get_all_location_mappings(rotkehlchen_api_server)['entries']

    # delete the mapping of NEW2
    deleted_mapping = {
        'location_symbol': all_mappings[0]['location_symbol'],
        'location': all_mappings[0]['location'],
    }
    response = requests.delete(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={
            'entries': [deleted_mapping],
        },
    )
    result = assert_proper_response_with_result(response)
    assert result is True

    result = _get_all_location_mappings(rotkehlchen_api_server)
    all_mappings_after_deletion = result['entries']
    assert len(all_mappings_after_deletion) == result['entries_found'] == 1499
    assert all_mappings[0] not in all_mappings_after_deletion


def test_location_asset_mappings_pagination(rotkehlchen_api_server: 'APIServer') -> None:
    """Test pagination in location asset mappings APIs."""
    all_mappings = _get_all_location_mappings(rotkehlchen_api_server)['entries']

    # pagination limit works
    response = requests.post(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={
            'offset': 0,
            'limit': 1,
        },
    )
    result = assert_proper_response_with_result(response=response)
    assert result['entries'] == [all_mappings[0]]
    assert result['entries_found'] == 1500

    # pagination offset works
    response = requests.post(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={
            'offset': 1,
            'limit': 1,
        },
    )
    result = assert_proper_response_with_result(response=response)
    assert result['entries'] == [all_mappings[1]]
    assert result['entries_found'] == 1500


def test_location_asset_mappings_errors(rotkehlchen_api_server: 'APIServer') -> None:
    """Test the conflict errors in location asset mappings APIs."""
    # add a mapping that already exists and expect failure
    response = requests.put(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={
            'entries': [{
                'asset': 'BCH',
                'location': 'binance',
                'location_symbol': 'BCHABC',
            }],
        },
    )
    assert_error_response(
        response=response,
        status_code=HTTPStatus.CONFLICT,
        contained_in_msg=(
            'Failed to add the location asset mapping of BCHABC in binance because it already exists in the DB.'  # noqa: E501
        ),
    )

    # delete a mapping that does not exist and expect failure
    response = requests.delete(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={
            'entries': [{
                'location_symbol': 'DNE',
                'location': 'kraken',
            }],
        },
    )
    assert_error_response(
        response=response,
        status_code=HTTPStatus.CONFLICT,
        contained_in_msg=(
            'Failed to delete the location asset mapping of DNE in kraken because it does not exist in the DB.'  # noqa: E501
        ),
    )

    # update a mapping that does not exist and expect failure
    response = requests.patch(
        api_url_for(
            rotkehlchen_api_server,
            'locationassetmappingsresource',
        ),
        json={
            'entries': [{
                'asset': 'eip155:1/erc20:0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',
                'location_symbol': 'DNE',
                'location': 'kraken',
            }],
        },
    )
    assert_error_response(
        response=response,
        status_code=HTTPStatus.CONFLICT,
        contained_in_msg=(
            'Failed to update the location asset mapping of DNE in kraken because it does not exist in the DB.'  # noqa: E501
        ),
    )
