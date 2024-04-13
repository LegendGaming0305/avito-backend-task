from rest_framework.views import exception_handler

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
 
    handlers = {
        'NotAuthenticated': _handle_permission_error,
        'IndexError': _handle_server_error,
        'ValidationError': _handle_validation_error,
    }

    exception_class = exc.__class__.__name__

    if response is not None:
        response.data['status_code'] = response.status_code

    res = exception_handler(exc, context)

    if exception_class in handlers:
        detail = handlers[exception_class](exc, context, res)
        response.data['description'] = detail
        try:
            del response.data['detail']
        except Exception:
            pass
    else:
        message = str(exc)
    print(exception_class)
    return response


def _handle_permission_error(exc, context, response):
    return 'Пользователь не имеет доступа'

def _handle_server_error(exc, context, response):
    return 'Внутренняя ошибка сервера'

def _handle_validation_error(exc, context, response):
    return 'Некорректные данные'