from unittest.mock import patch

import pytest

from awspub.common import _get_client, _get_regions, _split_partition


@pytest.mark.parametrize(
    "input,expected_output",
    [
        ("123456789123", ("aws", "123456789123")),
        ("aws:123456789123", ("aws", "123456789123")),
        ("aws-cn:123456789123", ("aws-cn", "123456789123")),
        ("aws-us-gov:123456789123", ("aws-us-gov", "123456789123")),
        (
            "arn:aws:organizations::123456789012:organization/o-123example",
            ("aws", "arn:aws:organizations::123456789012:organization/o-123example"),
        ),
        (
            "arn:aws:organizations::123456789012:ou/o-123example/ou-1234-5example",
            ("aws", "arn:aws:organizations::123456789012:ou/o-123example/ou-1234-5example"),
        ),
        (
            "arn:aws-cn:organizations::123456789012:organization/o-123example",
            ("aws-cn", "arn:aws-cn:organizations::123456789012:organization/o-123example"),
        ),
        (
            "arn:aws-cn:organizations::123456789012:ou/o-123example/ou-1234-5example",
            ("aws-cn", "arn:aws-cn:organizations::123456789012:ou/o-123example/ou-1234-5example"),
        ),
        (
            "arn:aws-us-gov:organizations::123456789012:organization/o-123example",
            ("aws-us-gov", "arn:aws-us-gov:organizations::123456789012:organization/o-123example"),
        ),
        (
            "arn:aws-us-gov:organizations::123456789012:ou/o-123example/ou-1234-5example",
            ("aws-us-gov", "arn:aws-us-gov:organizations::123456789012:ou/o-123example/ou-1234-5example"),
        ),
    ],
)
def test_common__split_partition(input, expected_output):
    assert _split_partition(input) == expected_output


@pytest.mark.parametrize(
    "regions_in_partition,configured_regions,expected_output",
    [
        (["region-1", "region-2"], ["region-1", "region-3"], ["region-1"]),
        (["region-1", "region-2", "region-3"], ["region-4", "region-5"], []),
        (["region-1", "region-2"], [], ["region-1", "region-2"]),
    ],
)
def test_common__get_regions(regions_in_partition, configured_regions, expected_output):
    with patch("boto3.client") as bclient_mock:
        instance = bclient_mock.return_value
        instance.describe_regions.return_value = {"Regions": [{"RegionName": r} for r in regions_in_partition]}

        assert _get_regions("", configured_regions) == expected_output


@pytest.mark.parametrize(
    "service,args,expected_region",
    [
        ("ec2", {"region_name": "us-west-1"}, "us-west-1"),
        ("s3", {"region_name": "eu-central-1"}, "eu-central-1"),
    ],
)
def test_get_client_with_args(service, args, expected_region):

    with patch("boto3.client") as client_mock:
        _get_client(service, **args)

        client_mock.assert_called_once_with(service, **args)
        _, called_kwargs = client_mock.call_args
        assert called_kwargs["region_name"] == expected_region


def test_get_client_without_args():

    with patch("boto3.client") as client_mock:
        _get_client("s3")

        client_mock.assert_called_once_with(
            "s3",
        )


def test_get_client_with_credentials_in_env(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test_access_key")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret_key")

    with patch("boto3.client") as client_mock:
        _get_client("s3")

        client_mock.assert_called_once_with(
            "s3",
            aws_access_key_id="test_access_key",
            aws_secret_access_key="test_secret_key",
        )
