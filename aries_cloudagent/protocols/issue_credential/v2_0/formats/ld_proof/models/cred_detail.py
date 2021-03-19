"""Linked data proof verifiable credential detail artifacts to attach to RFC 453 messages."""


from marshmallow import fields, Schema

from .......messaging.valid import INDY_ISO8601_DATETIME, UUIDFour
from .......vc.vc_ld.models.credential_schema import LDCredentialSchema


class CredentialStatusOptionsSchema(Schema):
    """Linked data proof credential status options schema."""

    type = fields.Str(
        required=True,
        description="Credential status method type to use for the credential. Should match status method registered in the Verifiable Credential Extension Registry",
        example="CredentialStatusList2017",
    )


class LDProofVCDetailOptions(Schema):
    """Linked data proof verifiable credential options schema."""

    proof_type = fields.Str(
        data_key="proofType",
        required=True,
        description="The proof type used for the proof. Should match suites registered in the Linked Data Cryptographic Suite Registry",
        example="Ed25519Signature2018",
    )

    proof_purpose = fields.Str(
        data_key="proofPurpose",
        required=False,
        default="assertionMethod",
        description="The proof purpose used for the proof. Should match proof purposes registered in the Linked Data Proofs Specification",
        example="assertionMethod",
    )

    created = fields.Str(
        required=False,
        description="The date and time of the proof (with a maximum accuracy in seconds). Defaults to current system time",
        **INDY_ISO8601_DATETIME,
    )

    domain = fields.Str(
        required=False,
        description="The intended domain of validity for the proof",
        example="example.com",
    )

    challenge = fields.Str(
        required=False,
        description="A challenge to include in the proof. SHOULD be provided by the requesting party of the credential (=holder)",
        example=UUIDFour.EXAMPLE,
    )

    credential_status = fields.Nested(
        CredentialStatusOptionsSchema,
        data_key="credentialStatus",
        required=False,
        description="The credential status mechanism to use for the credential. Omitting the property indicates the issued credential will not include a credential status",
    )


class LDProofVCDetail(Schema):
    """Linked data proof verifiable credential detail schema."""

    credential = fields.Nested(
        LDCredentialSchema,
        required=True,
        description="Detail of the JSON-LD Credential to be issued",
    )

    options = fields.Nested(
        LDProofVCDetailOptions,
        required=True,
        description="Options for specifying how the linked data proof is created.",
    )
