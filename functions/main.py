def a_set(request):
    import ddns_gcp_functions.a_set
    return run(ddns_gcp_functions.a_set,request)

def run(m,request):
    import os
    import flask
    run_args = {}
    run_args['setting_path'] = os.environ['SETTING_PATH']
    run_args['request_json'] = request.get_data()
    ret = m.run(**run_args)
    response = flask.Response(
        response = ret['body'] if 'body' in ret else None,
        status = ret['statusCode'],
    )
    return response
