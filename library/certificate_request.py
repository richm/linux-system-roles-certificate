# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "status": ["preview"],
    "supported_by": "community",
}

DOCUMENTATION = """
---
module: certificate_request
short_description: Manage SSL/TLS certificates.
description:
  - The C(certificate_request) module takes a name, desired
    certificate request attributes and certificate properties.
  - The request is generated and sent to the CA to sign.

options:
  name:
    description:
      - Name of the certificate. Can be either a full path
        where files will be stored or a just a simple file name
        to be stored in I(directory).
    required: true
  dns:
    description:
      - Domain (or list of domains) to be included in the
        certificate. Also can provide the default value for
        common_name.
    required: false
  ca:
    description:
      - CA that will issue the certificate. The available options
        will vary depending on each provider.
    required: true
  provider:
    description:
      - The underlying method used to request and manage the
        certificate.
    required: false
    default: certmonger
  directory:
    description:
      - Directory where certificate and key will be stored. Only used
        if I(name) is not an absolute path.
    required: false
    default: /etc/pki/tls
author:
  - Sergio Oliveira Campos (@seocam)
"""

EXAMPLES = """
# Certificate for single domain
- name: Ensure certificate exists for www.example.com
  certificate_request:
    name: single-example
    dns: www.example.com
    ca: self-sign

# Certificate for multiple domains
- name: Ensure certificate exists for multiple domains
  certificate_request:
    name: many-example
    dns:
      - www.example.com
      - example.com
    ca: self-sign
"""

RETURN = ""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.certificate.providers import PROVIDERS


class CertificateRequestModule(AnsibleModule):
    """Certificate Request Module.

    This module is responsible for converging SSL/TLS certificates
    using providers.
    """

    def __init__(self, *args, **kwargs):
        argument_spec = kwargs.get("argument_spec", {})
        argument_spec.update(self._get_argument_spec())

        self._provider = None
        super(CertificateRequestModule, self).__init__(argument_spec, *args, **kwargs)

        # Set to True to see logs on the Host machine using `journalctl -f`
        #   TIP: "grep certificate_request" will help you find relevant entries.
        self._debug = False

    @staticmethod
    def _get_argument_spec():
        """Return a dict with the module arguments."""
        return dict(
            name=dict(type="str", required=True),
            dns=dict(type="list"),
            ca=dict(type="str", required=True),
            directory=dict(type="str", default="/etc/pki/tls"),
            provider=dict(type="str", default="certmonger"),
        )

    @property
    def provider(self):
        """Instantiate and return the proper provider for the run."""
        if self._provider is None:
            provider_name = self.params.get("provider")
            provider_cls = dict(PROVIDERS).get(provider_name)
            if provider_cls is None:
                self.fail_json(
                    msg="Chosen provider '{}' is not available.".format(provider_name),
                )
            self._provider = provider_cls(ansible_module=self)

        return self._provider

    def run(self):
        """Run the module using the chosen provider."""
        return self.provider.run(self.check_mode)


def main():
    """Instantiate and execute the Certificate module."""
    CertificateRequestModule(supports_check_mode=True).run()


if __name__ == "__main__":
    main()