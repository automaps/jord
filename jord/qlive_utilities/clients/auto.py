from functools import partial
from typing import Callable

from jord.qlive_utilities.client import QliveClient
from jord.qlive_utilities.procedures import QliveRPCMethodEnum, QliveRPCMethodMap
from jord.qlive_utilities.serialisation import build_package
from .arguments import partial_satisfied

__doc__ = r"""Warning this client a no client-side validation, which might result in server-side exceptions"""

__all__ = ["AutoQliveClient"]


class AutoQliveClient(QliveClient):
    """
    Has no client side validation of data, but exposes function if available in QliveRPCMethodEnum and
    QliveRPCMethodMap
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for method in QliveRPCMethodEnum:
            if method in QliveRPCMethodMap:
                actual_callable = QliveRPCMethodMap[method]

                if False:
                    partial_build_package = partial(build_package, method)
                    if False and partial_satisfied(
                        partial_build_package
                    ):  # TODO: RESOLVE PARTIAL APPLICATION SATISFACTION.

                        def a():
                            """ """
                            self.send(partial_build_package())

                        rpc_method = a
                    elif True:

                        def a(*args):
                            """

                            :param args:
                            :type args:
                            """
                            self.send(partial_build_package(*args))

                        rpc_method = a
                    elif False:

                        def a(**kwargs):
                            """

                            :param kwargs:
                            :type kwargs:
                            """
                            self.send(partial_build_package(**kwargs))

                        rpc_method = a
                    elif False:

                        def a(*args, **kwargs):
                            """

                            :param args:
                            :type args:
                            :param kwargs:
                            :type kwargs:
                            """
                            self.send(partial_build_package(*args, **kwargs))

                        rpc_method = a
                    else:
                        raise NotImplementedError
                elif False:
                    rpc_method = lambda *args: self.send(
                        partial(build_package, method)(*args)
                    )
                elif False:
                    rpc_method = lambda *args: self.send(build_package(method, *args))
                else:

                    def wrapped(method_, *args_, **_kwargs) -> Callable:
                        """

                        :param method_:
                        :type method_:
                        :param args_:
                        :type args_:
                        :param _kwargs:
                        :type _kwargs:
                        :return:
                        :rtype:
                        """
                        return self.send(build_package(method_, *args_, **_kwargs))

                    rpc_method = partial(wrapped, method)

                rpc_method.__doc__ = actual_callable.__doc__
                setattr(self, method.value, rpc_method)


if __name__ == "__main__":
    # QliveClient().clear_all()
    # QliveClient().remove_layers()
    # print(QliveClient().clear_all.__doc__)
    # print(QliveClient().__dict__)
    def uahdsuh():
        """ """
        with AutoQliveClient() as qlive:
            qlive.add_wkts({"a": "POINT (-66.86 10.48)"})

    # QliveClient().add_dataframe(None)

    uahdsuh()
