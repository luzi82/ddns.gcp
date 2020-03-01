import json

def e4(fail_code, fail_msg=None):
    return {
        'statusCode': 400,
        'body': json.dumps({
            'RESULT': 'FAIL',
            'FAIL_CODE': fail_code,
            'FAIL_MSG': fail_msg,
        }),
    }

def ok(body=None):
    return {
        'statusCode': 200,
        'body': body,
    }
