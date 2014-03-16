import socket


def create_socket_from_text(text):
    sock_file = None

    if text.startswith('tcp://'):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        l = text[6:].split(':')
        return {
            'sock': sock,
            'bind_to': (l[0], int(l[1]))
        }
    elif text.startswith('tcp6://'):
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        l = text[7:]
        port_sep = l.rfind(':')
        addr, port = l[:port_sep].strip('[]'), int(l[port_sep + 1:])
        return {
            'sock': sock,
            'bind_to': (addr, port)
        }
    elif text.startswith('sock://'):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock_file = text[7:]
        return {
            'sock': sock,
            'bind_to': sock_file,
            'file': sock_file
        }
    else:
        raise NotImplementedError('Unknown listen type')


def socket_bind_from_text(text):
    sock_info = create_socket_from_text(text)
    sock_info['sock'].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_info['sock'].bind(sock_info['bind_to'])
    sock_info['sock'].setblocking(0)
    sock_info['sock'].listen(5)
    return sock_info['sock'], sock_info.get('file', None)


def socket_connect_from_text(text):
    sock_info = create_socket_from_text(text)
    sock_info['sock'].connect(sock_info['bind_to'])
    return sock_info['sock']
