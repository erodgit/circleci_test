*** Settings ***
Library         OperatingSystem
Library         Collections
Library         ../src/rippled_client.py    WITH NAME   RippledClient
Suite Setup     Initialize Globals

*** Variables ***
${HOST}             18.216.216.236
${RIPPLED_PORT}     30006
${RIPPLED_VERSION}  0.80.0
${FUND_AMOUNT}      5000000000
${SEND_AMOUNT}      10000
${MULTI_SIGN_FEE}   50000000
*** Test Cases ***
Rippled is up
    [Documentation]  Confirm that rippled is up and responding and the multi-sign feature is enabled
    ${RIPPlED} is healthy

Rippled version is expected
    [Documentation]  Confirm that rippled version is what we expect
    ${version}=      Get ${RIPPLED} version

    Should Be Equal     ${RIPPLED_VERSION}      ${version}

Send money to multisign account
    ${signer_list}=    Configure multisign on ${MS_ACCOUNT} with 8 signers and quorum 8
    Log                SIGNER List: ${signer_list}

    Send ${send_amount} from multisign account ${MS_ACCOUNT} to ${GEN_ACCOUNT} using ${signer_list}

*** Keywords ***
Initialize Globals
    ${RIPPLED}=       Get rippled client
    set suite variable      ${RIPPLED}

    ${GEN_ACCOUNT}=   RippledClient.get_account    ${RIPPLED}    genesis
    set suite variable      ${GEN_ACCOUNT}

    ${MS_ACCOUNT}=    Fund new account
    set suite variable      ${MS_ACCOUNT}

Configure multisign on ${ms_account} with ${signer_count} signers and quorum ${quorum}
    ${signer_weights}=  Create Dictionary
    : FOR   ${INDEX}   IN RANGE     0   ${signer_count}
    \   ${signer_account}=    RippledClient.get_account    ${RIPPLED}    new
    \   Set to dictionary   ${signer_weights}      ${signer_account}   1

    ${signer_list}=     Configure multisign on ${ms_account} given ${signer_weights} and quorum ${quorum}
    [Return]    ${signer_list}

Configure multisign given ${signer_weights} and quorum ${quorum}
    ${ms_account}=    Fund new account

    Configure multisign on ${ms_account} given ${signer_weights} and quorum ${quorum}

    [Return]    ${ms_account}

Configure multisign on ${ms_account} given ${signer_weights} and quorum ${quorum}
    ${signer_list}=     Get Dictionary Keys     ${signer_weights}
    ${signer_count}=    Get Length              ${signer_list}

    Log                Weights: ${signer_weights}
    Log                List: ${signer_list}

    call method        ${ms_account}        config_multi_sign   ${quorum}   ${signer_weights}

    ${objects}=        call method      ${RIPPLED}      account_objects     ${ms_account.id}
    ${obj_list}=       call method      ${objects}      get     account_objects
    ${objects}=        Get From List    ${obj_list}     0
    ${signers}=        call method      ${objects}      get     SignerEntries
    ${entry_count}=    Get Length       ${signers}
    Log                Objects: ${objects}
    Should Be True     ${entry_count} == ${signer_count}     Error: ${signer_count} signers not configured

    [Return]    ${signer_list}

Send ${amount} from multisign account ${src_account} to ${dst_account} using ${signer_list}
    ${tx_hash}=        call method      ${src_account}     send_multi_sign_payment   ${amount}   ${dst_account}  ${signer_list}  ${MULTI_SIGN_FEE}
    Log                TX Hash: ${tx_hash}

    ${resp}=           call method     ${RIPPLED}      confirm_tx   ${tx_hash}
    Log                TX Resp: ${resp}

Get rippled client
    ${rippled}=       RippledClient.get_rippled_client    ${HOST}     ${RIPPLED_PORT}
    [Return]    ${rippled}

${rippled} is healthy
    ${status}=         call method     ${rippled}          get_server_info
    ${ms_status}=      call method     ${rippled}          multisign_status

    Should Be True     ${ms_status}

Get ${rippled} version
    ${version}=         call method     ${rippled}          get_rippled_version

    [Return]    ${version}

Fund new account
    ${new_account}=       RippledClient.get_account    ${RIPPLED}    new

    ${result}=         call method     ${GEN_ACCOUNT}   send_payment     ${FUND_AMOUNT}  ${new_account}
    Should Be True     ${result}

    ${new_balance}=    Get ${new_account} balance
    Should Be True  ${new_balance} == ${FUND_AMOUNT}

    [Return]    ${new_account}

Get ${account} balance
    ${balance}=     call method     ${account}   get_balance

    [Return]    ${balance}
