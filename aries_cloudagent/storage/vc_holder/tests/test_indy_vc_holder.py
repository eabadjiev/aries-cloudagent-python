import pytest


from ....config.injection_context import InjectionContext
from ....indy.sdk.profile import IndySdkProfileManager
from ....ledger.indy import IndySdkLedgerPool
from ....wallet.indy import IndySdkWallet

from ..base import VCHolder
from ..vc_record import VCRecord

from . import test_in_memory_vc_holder as in_memory


VC_CONTEXT = "https://www.w3.org/2018/credentials/v1"
VC_TYPE = "https://www.w3.org/2018/credentials#VerifiableCredential"
VC_SUBJECT_ID = "did:example:ebfeb1f712ebc6f1c276e12ec21"
VC_PROOF_TYPE = "Ed25519Signature2018"
VC_ISSUER_ID = "https://example.edu/issuers/14"
VC_SCHEMA_ID = "https://example.org/examples/degree.json"
VC_GIVEN_ID = "http://example.edu/credentials/3732"


async def make_profile():
    key = await IndySdkWallet.generate_wallet_key()
    context = InjectionContext()
    context.injector.bind_instance(IndySdkLedgerPool, IndySdkLedgerPool("name"))
    return await IndySdkProfileManager().provision(
        context,
        {
            "auto_recreate": True,
            "auto_remove": True,
            "name": "test-wallet",
            "key": key,
            "key_derivation_method": "RAW",  # much slower tests with argon-hashed keys
        },
    )


@pytest.fixture()
async def holder():
    profile = await make_profile()
    async with profile.session() as session:
        yield session.inject(VCHolder)
    await profile.close()


def test_record() -> VCRecord:
    return VCRecord(
        contexts=[
            VC_CONTEXT,
            "https://www.w3.org/2018/credentials/examples/v1",
        ],
        expanded_types=[
            VC_TYPE,
            "https://example.org/examples#UniversityDegreeCredential",
        ],
        schema_ids=[VC_SCHEMA_ID],
        issuer_id=VC_ISSUER_ID,
        subject_ids=[VC_SUBJECT_ID],
        proof_types=[VC_PROOF_TYPE],
        given_id=VC_GIVEN_ID,
        cred_tags={"tag": "value"},
        cred_value={"...": "..."},
    )


@pytest.mark.indy
class TestIndySdkVCHolder(in_memory.TestInMemoryVCHolder):
    # run same test suite with different holder fixture
    @pytest.mark.asyncio
    async def test_tag_query(self, holder: VCHolder):
        test_uri_list = [
            "https://www.w3.org/2018/credentials#VerifiableCredential",
            "https://example.org/examples#UniversityDegreeCredential",
        ]
        test_query = holder.build_type_or_schema_query(test_uri_list)
        assert test_query == {
            "$and": [
                {
                    "$or": [
                        {
                            "type:https://www.w3.org/2018/credentials#VerifiableCredential": "1"
                        },
                        {
                            "schm:https://www.w3.org/2018/credentials#VerifiableCredential": "1"
                        },
                    ]
                },
                {
                    "$or": [
                        {
                            "type:https://example.org/examples#UniversityDegreeCredential": "1"
                        },
                        {
                            "schm:https://example.org/examples#UniversityDegreeCredential": "1"
                        },
                    ]
                },
            ]
        }
        record = test_record()
        await holder.store_credential(record)

        search = holder.search_credentials(pd_uri_list=test_uri_list)
        rows = await search.fetch()
        assert rows == [record]
