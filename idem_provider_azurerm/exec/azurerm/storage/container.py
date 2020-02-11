# -*- coding: utf-8 -*-
'''
Azure Resource Manager (ARM) Blob Container Operations Execution Module

.. versionadded:: 1.0.0

:maintainer: <devops@eitr.tech>
:maturity: new
:depends:
    * `azure <https://pypi.python.org/pypi/azure>`_ >= 4.0.0
    * `azure-common <https://pypi.python.org/pypi/azure-common>`_ >= 1.1.23
    * `azure-mgmt <https://pypi.python.org/pypi/azure-mgmt>`_ >= 4.0.0
    * `azure-mgmt-compute <https://pypi.python.org/pypi/azure-mgmt-compute>`_ >= 4.6.2
    * `azure-mgmt-network <https://pypi.python.org/pypi/azure-mgmt-network>`_ >= 4.0.0
    * `azure-mgmt-resource <https://pypi.python.org/pypi/azure-mgmt-resource>`_ >= 2.2.0
    * `azure-mgmt-storage <https://pypi.python.org/pypi/azure-mgmt-storage>`_ >= 2.0.0
    * `azure-mgmt-web <https://pypi.python.org/pypi/azure-mgmt-web>`_ >= 0.35.0
    * `azure-storage <https://pypi.python.org/pypi/azure-storage>`_ >= 0.36.0
    * `msrestazure <https://pypi.python.org/pypi/msrestazure>`_ >= 0.6.1
:platform: linux

:configuration: This module requires Azure Resource Manager credentials to be passed as keyword arguments
    to every function in order to work properly.

    Required provider parameters:

    if using username and password:
      * ``subscription_id``
      * ``username``
      * ``password``

    if using a service principal:
      * ``subscription_id``
      * ``tenant``
      * ``client_id``
      * ``secret``

    Optional provider parameters:

**cloud_environment**: Used to point the cloud driver to different API endpoints, such as Azure GovCloud.
    Possible values:
      * ``AZURE_PUBLIC_CLOUD`` (default)
      * ``AZURE_CHINA_CLOUD``
      * ``AZURE_US_GOV_CLOUD``
      * ``AZURE_GERMAN_CLOUD``
'''

# Python libs
from __future__ import absolute_import
import logging

try:
    from six.moves import range as six_range
except ImportError:
    six_range = range

# Azure libs
HAS_LIBS = False
try:
    import azure.mgmt.storage  # pylint: disable=unused-import
    from msrestazure.azure_exceptions import CloudError
    HAS_LIBS = True
except ImportError:
    pass

log = logging.getLogger(__name__)

async def clear_legal_hold(hub, name, account, resource_group, tags, **kwargs):
    '''
    .. versionadded:: 1.0.0

    Clears legal hold tags. Clearing the same or non-existent tag results in an idempotent operation. ClearLegalHold
        clears out only the specified tags in the request.

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    :param tags: Each tag should be 3 to 23 alphanumeric characters and is normalized to lower case at SRP.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.clear_legal_hold test_name test_account test_group test_tags

    '''
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        hold = storconn.blob_containers.clear_legal_hold(
            container_name=name,
            resource_group_name=resource_group,
            account_name=account,
            tags=tags
        )

        result = hold.as_dict()
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)
        result = {'error': str(exc)}

    return result


async def create(hub, name, account, resource_group, public_access=None, metadata=None, **kwargs):
    '''
    .. versionadded:: 1.0.0

    Creates a new container under the specified account as described by request body. The container resource includes
        metadata and properties for that container. It does not include a list of the blobs contained by the container.

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    :param public_access: Specifies whether data in the container may be accessed publicly and the level of access.
        Possible values include: 'Container', 'Blob', 'None'. Defaults to None.

    :param metadata: A name-value pair to associate with the container as metadata. Defaults to None.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.create test_name test_account test_group test_access test_metadata

    '''
    result = {}
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        container = storconn.blob_containers.create(
            container_name=name,
            account_name=account,
            resource_group_name=resource_group,
            public_access=public_access,
            metadata=metadata,
            **kwargs
        )

        result = container.as_dict()
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)
        result = {'error': str(exc)}
    except SerializationError as exc:
        result = {'error': 'The object model could not be parsed. ({0})'.format(str(exc))}

    return result


async def create_or_update_immutability_policy(hub, name, account, resource_group,
                                               immutability_period_since_creation_in_days, if_match=None, **kwargs):
    '''
    .. versionadded:: 1.0.0

    Creates or updates an unlocked immutability policy.

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    :param immutability_period_since_creation_in_days: The immutability period for the blobs in the container since the
        policy creation, in days.

    :param if_match: The entity state (ETag) version of the immutability policy to update. A value of "*" can be used
        to apply the operation only if the immutability policy already exists. If omitted, this operation will always
        be applied. Defaults to None.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.create_or_update_immutability_policy test_name test_account test_group test_period

    '''
    result = {}
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        policy = storconn.blob_containers.create_or_update_immutability_policy(
            container_name=name,
            account_name=account,
            resource_group_name=resource_group,
            immutability_period_since_creation_in_days=immutability_period_since_creation_in_days,
            if_match=if_match,
            **kwargs
        )

        result = policy.as_dict()
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)
        result = {'error': str(exc)}
    except SerializationError as exc:
        result = {'error': 'The object model could not be parsed. ({0})'.format(str(exc))}

    return result


async def delete(hub, name, account, resource_group, **kwargs):
    '''
    .. versionadded:: 1.0.0

    Deletes specified container under its account.

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.delete test_name test_account test_group

    '''
    result = False
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        container = storconn.blob_containers.delete(
            container_name=name,
            account_name=account,
            resource_group_name=resource_group
        )

        result = True
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)

    return result


async def delete_immutability_policy(hub, name, account, resource_group, if_match, **kwargs):
    '''
    .. versionadded:: 1.0.0

    Aborts an unlocked immutability policy. The response of delete has immutabilityPeriodSinceCreationInDays set to 0.
        ETag in If-Match is required for this operation. Deleting a locked immutability policy is not allowed, only way
        is to delete the container after deleting all blobs inside the container.

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    :param if_match: The entity state (ETag) version of the immutability policy to update. A value of "*" can be used
        to apply the operation only if the immutability policy already exists. If omitted, this operation will always
        be applied.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.delete_immutability_policy test_name test_account test_group test_if_match

    '''
    result = False
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        policy = storconn.blob_containers.delete_immutability_policy(
            container_name=name,
            account_name=account,
            resource_group_name=resource_group,
            if_match=if_match
        )

        result = True
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)

    return result


async def extend_immutability_policy(hub, name, account, resource_group, immutability_period_since_creation_in_days,
                                     if_match, **kwargs):
    '''
    .. versionadded:: 1.0.0

    Extends the immutabilityPeriodSinceCreationInDays of a locked immutabilityPolicy. The only action allowed on a
        Locked policy will be this action. ETag in If-Match is required for this operation.

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    :param immutability_period_since_creation_in_days: The immutability period for the blobs in the container since the
        policy creation, in days.

    :param if_match: The entity state (ETag) version of the immutability policy to update. A value of "*" can be used
        to apply the operation only if the immutability policy already exists. If omitted, this operation will always
        be applied.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.extend_immutability_policy test_name test_account test_group test_period test_if_match

    '''
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        policy = storconn.blob_containers.extend_immutability_policy(
            container_name=name,
            account_name=account,
            resource_group_name=resource_group,
            immutability_period_since_creation_in_days=immutability_period_since_creation_in_days,
            if_match=if_match,
            **kwargs
        )

        result = policy
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)
        result = {'error': str(exc)}

    return result


async def get(hub, name, account, resource_group, **kwargs):
    '''
    .. versionadded:: 1.0.0

    Gets properties of a specified container.

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.get test_name test_account test_group

    '''
    result = {}
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        container = storconn.blob_containers.get(
            container_name=name,
            account_name=account,
            resource_group_name=resource_group
        )

        result = container.as_dict()
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)
        result = {'error': str(exc)}

    return result


async def get_immutability_policy(hub, name, account, resource_group, if_match=None, **kwargs):
    '''
    .. versionadded:: 1.0.0

    Gets properties of a specified container.

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    :param if_match: The entity state (ETag) version of the immutability policy to update. A value of "*" can be used
        to apply the operation only if the immutability policy already exists. If omitted, this operation will always
        be applied. Defaults to None.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.get_immutability_policy test_name test_account test_group test_if_match

    '''
    result = {}
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        policy = storconn.blob_containers.get_immutability_policy(
            container_name=name,
            account_name=account,
            resource_group_name=resource_group,
            if_match=if_match
        )

        result = policy.as_dict()
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)
        result = {'error': str(exc)}

    return result


async def lease(hub, name, account, resource_group, action, **kwargs):
    '''
    .. versionadded:: 1.0.0

    The Lease Container operation establishes and manages a lock on a container for delete operations. The lock duration
        can be 15 to 60 seconds, or can be infinite.

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    :param action: Specifies the lease action. Can be one of the available actions. Possible values include: 'Acquire',
        'Renew', 'Change', 'Release', 'Break'

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.lease test_name test_account test_group test_action

    '''
    result = {}
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        leasemodel = await hub.exec.utils.azurerm.create_object_model(
            'storage',
            'LeaseContainerRequest',
            action=action,
            **kwargs
        )
    except TypeError as exc:
        result = {'error': 'The object model could not be built. ({0})'.format(str(exc))}
        return result

    try:
        container = storconn.blob_containers.lease(
            container_name=name,
            account_name=account,
            resource_group_name=resource_group,
            parameters=leasemodel
        )

        result = policy.as_dict()
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)
        result = {'error': str(exc)}

    return result


async def list_(hub, account, resource_group, **kwargs):
    '''
    .. versionadded:: 1.0.0

    Lists all containers and does not support a prefix like data plane. Also SRP today does not return continuation
        token.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.list test_account test_group

    '''
    result = {}
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        containers = storconn.blob_containers.list(
            account_name=account,
            resource_group_name=resource_group
        )

        containers_list = containers.as_dict().get('value', [])
        for container in containers_list:
            result[container['name']] = container
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)
        result = {'error': str(exc)}

    return result


async def lock_immutability_policy(hub, name, account, resource_group, if_match, **kwargs):
    '''
    .. versionadded:: 1.0.0

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    :params if_match: The entity state (ETag) version of the immutability policy to update. A value of "*" can be used
        to apply the operation only if the immutability policy already exists. If omitted, this operation will always
        be applied.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.lock_immutability_policy test_name test_account test_group test_if_match

    '''
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        policy = storconn.blob_containers.lock_immutability_policy(
            container_name=name,
            account_name=account,
            resource_group_name=resource_group,
            if_match=if_match,
            **kwargs
        )

        result = policy
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)
        result = {'error': str(exc)}

    return result


async def set_legal_hold(hub, name, account, resource_group, tags, **kwargs):
    '''
    .. versionadded:: 1.0.0

    Sets legal hold tags. Setting the same tag results in an idempotent operation. SetLegalHold follows an append
        pattern and does not clear out the existing tags that are not specified in the request.

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    :param tags: Each tag should be 3 to 23 alphanumeric characters and is normalized to lower case at SRP.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.set_legal_hold test_name test_account test_group test_tags

    '''
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        hold = storconn.blob_containers.set_legal_hold(
            container_name=name,
            resource_group_name=resource_group,
            account_name=account,
            tags=tags
        )

        result = hold.as_dict()
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)
        result = {'error': str(exc)}

    return result


async def update(hub, name, account, resource_group, public_access=None, metadata=None, **kwargs):
    '''
    .. versionadded:: 1.0.0

    Updates container properties as specified in request body. Properties not mentioned in the request will be
        unchanged. Update fails if the specified container doesn't already exist.

    :param name: The name of the blob container within the specified storage account. Blob container names must be
        between 3 and 63 characters in length and use numbers, lower-case letters and dash (-) only. Every dash (-)
        character must be immediately preceded and followed by a letter or number.

    :param account: The name of the storage account within the specified resource group. Storage account names must be
        between 3 and 24 characters in length and use numbers and lower-case letters only.

    :param resource_group: The name of the resource group within the user's subscription. The name is case insensitive.

    :param public_access: Specifies whether data in the container may be accessed publicly and the level of access.
        Possible values include: 'Container', 'Blob', 'None'. Defaults to None.

    :param metadata: A name-value pair to associate with the container as metadata. Defaults to None.

    CLI Example:

    .. code-block:: bash

        azurerm.storage.container.update test_name test_account test_group test_access test_metadata

    '''
    storconn = await hub.exec.utils.azurerm.get_client('storage', **kwargs)

    try:
        container = storconn.blob_containers.update(
            container_name=name,
            account_name=account,
            resource_group_name=resource_group,
            public_access=public_access,
            metadata=metadata,
            **kwargs
        )

        result = container.as_dict()
    except CloudError as exc:
        await hub.exec.utils.azurerm.log_cloud_error('storage', str(exc), **kwargs)
        result = {'error': str(exc)}
    except SerializationError as exc:
        result = {'error': 'The object model could not be parsed. ({0})'.format(str(exc))}

    return result
